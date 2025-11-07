import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
from typing import TypedDict, List
from youtube_transcript_api import YouTubeTranscriptApi
from tavily import TavilyClient


class AgentState(TypedDict):
    transcript_text: str
    transcript_snippets: List[dict]
    vocab_explanations: List[dict]
    context_entities: List[dict]

tavily = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))

def find_and_explain_words(state: AgentState):
    print("--- NODE: find_and_explain_words ---")
    full_transcript = state["transcript_text"]
    transcript_snippets = state.get("transcript_snippets", [])

    try:
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            print("Error: GROQ_API_KEY not set.")
            return {"vocab_explanations": [], "context_entities": []}

        llm = ChatGroq(
            model="llama-3.1-8b-instant",
            groq_api_key=api_key,
            temperature=0
        )
        json_llm = llm.bind(response_format={"type": "json_object"})
    except Exception as e:
        print(f"Error initializing Groq LLM: {e}")
        return {"vocab_explanations": [], "context_entities": []}

    vocab_prompt = """
    You are an expert lexicographer and linguist. A user has provided a video transcript.
    Identify ONLY genuinely difficult, uncommon, or technical English words.

    RULES:
    1. Do NOT explain simple, common, or conversational words.
    2. Do NOT include names or proper nouns.
    3. Do NOT include typos or invented words.
    4. Include only advanced, technical, or rarely used real English words.

    For EACH selected word, respond in JSON format with:
    {
      "explanations": [
        {
          "term": "word",
          "explanation": "definition in 15–30 words",
          "synonyms": ["easier_word1", "easier_word2", "easier_word3"]
        }
      ]
    }
    """

    messages = [
        SystemMessage(content=vocab_prompt),
        HumanMessage(content=f"Transcript:\n\n{full_transcript}\n\nIdentify difficult words and synonyms.")
    ]

    try:
        response = json_llm.invoke(messages)
        vocab_data = json.loads(response.content)
        vocab_explanations = vocab_data.get("explanations", [])
    except Exception as e:
        print(f"[Error in vocab extraction] {e}")
        vocab_explanations = []

    vocab_with_timestamps = []
    for item in vocab_explanations:
        term = item.get("term", "").lower().strip()
        if not term:
            continue
        timestamp = None
        for snippet in transcript_snippets:
            if term in snippet["text"].lower().split():
                timestamp = snippet["start"]
                break
        if timestamp is not None:
            vocab_with_timestamps.append({
                "term": item.get("term"),
                "explanation": item.get("explanation"),
                "synonyms": item.get("synonyms", []),
                "timestamp": round(timestamp, 2)
            })

    context_prompt = """
    You are a historical context identifier.
    From the following transcript, identify up to 5 named entities that represent
    major historical figures, events, scientific discoveries, wars, organizations, or significant topics.

    For each entity, return this JSON format:
    {
      "context_entities": [
        {
          "entity": "string",
          "type": "person | event | organization | concept",
          "timestamp": number
        }
      ]
    }
    """

    context_messages = [
        SystemMessage(content=context_prompt),
        HumanMessage(content=f"Transcript:\n\n{full_transcript}\n\nList historical entities and topics mentioned.")
    ]

    try:
        context_response = json_llm.invoke(context_messages)
        context_data = json.loads(context_response.content)
        context_entities = context_data.get("context_entities", [])
    except Exception as e:
        print(f"[Error extracting entities] {e}")
        context_entities = []

    enriched_context = []
    for ent in context_entities:
        name = ent.get("entity")
        if not name:
            continue
        try:
            search_result = tavily.search(name, max_results=1, include_answer=True)
            summary = search_result.get("results", [{}])[0].get("answer", "No information found.")
        except Exception as e:
            summary = f"Error fetching info: {e}"
        enriched_context.append({
            "entity": name,
            "type": ent.get("type", "unknown"),
            "summary": summary,
            "timestamp": round(ent.get("timestamp", 0), 2)
        })

    print(f"✅ Generated Vocab: {len(vocab_with_timestamps)} | Context: {len(enriched_context)}")
    return {
        "vocab_explanations": vocab_with_timestamps,
        "context_entities": enriched_context
    }

workflow = StateGraph(AgentState)
workflow.add_node("find_and_explain_words", find_and_explain_words)
workflow.set_entry_point("find_and_explain_words")
workflow.add_edge("find_and_explain_words", END)
app_agent = workflow.compile()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

def get_youtube_transcript(video_id):
    try:
        api = YouTubeTranscriptApi()
        fetched_transcript = api.fetch(video_id, languages=['en'])
        snippets = fetched_transcript.snippets

        text = ""
        snippets_list = []
        for s in snippets:
            text += s.text + " "
            snippets_list.append({"text": s.text, "start": s.start, "duration": s.duration})

        return True, (text.strip(), snippets_list)
    except Exception as e:
        return False, {"error": str(e), "code": 500}

@app.route('/explain', methods=['POST'])
def explain():
    data = request.json
    video_id = data.get("youtube_id")
    start = float(data.get("start_time", 0))
    end = float(data.get("end_time", 0))

    print(f"\n--- New Request ---\nVideo: {video_id}, Start: {start}, End: {end}")

    success, result = get_youtube_transcript(video_id)
    if not success:
        return jsonify(result), result.get("code", 500)

    full_text, all_snippets = result

    filtered_snippets = [s for s in all_snippets if s["start"] < end and (s["start"] + s["duration"]) > start]
    filtered_text = " ".join([s["text"] for s in filtered_snippets]).strip()

    if not filtered_text:
        return jsonify({"error": "No transcript text found in given time range"}), 404

    inputs = {"transcript_text": filtered_text, "transcript_snippets": filtered_snippets}
    final_state = app_agent.invoke(inputs)
    return jsonify(final_state)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok", "message": "Server is running"}), 200

if __name__ == '__main__':
    print("🚀 Starting Flask server on http://127.0.0.1:5000")
    print("Ensure GROQ_API_KEY and TAVILY_API_KEY are set.")
    app.run(debug=True, port=5000)
