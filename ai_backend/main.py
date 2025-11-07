import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
from typing import TypedDict, List
import json
from youtube_transcript_api import YouTubeTranscriptApi

class AgentState(TypedDict):
    transcript_text: str
    transcript_snippets: List[dict]
    explanations: List[dict]

def find_and_explain_words(state: AgentState):
    print("--- NODE: find_and_explain_words ---")
    full_transcript = state["transcript_text"]
    transcript_snippets = state.get("transcript_snippets", [])

    try:
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            print("Error: GROQ_API_KEY not set.")
            return {"explanations": []}

        llm = ChatGroq(
            model="llama-3.1-8b-instant",
            groq_api_key=api_key,
            temperature=0
        )
        json_llm = llm.bind(response_format={"type": "json_object"})
    except Exception as e:
        print(f"Error initializing Groq LLM: {e}")
        return {"explanations": []}

    system_prompt = """
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

    Guidelines:
    - Provide 2–4 short synonyms or simpler equivalents in "synonyms".
    - If no synonyms exist, return an empty array.
    - If no valid difficult words are found, return {"explanations": []}.
    """

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(
            content=f"Transcript:\n\n{full_transcript}\n\nIdentify difficult or technical words with their meanings and synonyms."
        )
    ]

    try:
        response = json_llm.invoke(messages)
        response_data = json.loads(response.content)
        explanations = response_data.get("explanations", [])

        explanations_with_timestamps = []
        for explanation in explanations:
            term = explanation.get("term", "").lower().strip()
            if not term:
                continue

            timestamp = None
            for snippet in transcript_snippets:
                snippet_text = snippet["text"].lower()
                if term in snippet_text.split():
                    timestamp = snippet["start"]
                    break

            if timestamp is not None:
                explanations_with_timestamps.append({
                    "term": explanation.get("term"),
                    "explanation": explanation.get("explanation"),
                    "synonyms": explanation.get("synonyms", []),
                    "timestamp": round(timestamp, 2)
                })

        print(f"Generated explanations: {json.dumps(explanations_with_timestamps, indent=2)}")
        return {"explanations": explanations_with_timestamps}

    except Exception as e:
        print(f"Error calling LLM or parsing JSON: {e}")
        return {"explanations": []}

workflow = StateGraph(AgentState)
workflow.add_node("find_and_explain_words", find_and_explain_words)
workflow.set_entry_point("find_and_explain_words")
workflow.add_edge("find_and_explain_words", END)
app_agent = workflow.compile()

app = Flask(__name__)
CORS(app)

def get_youtube_transcript(video_id):
    try:
        api = YouTubeTranscriptApi()
        fetched_transcript = api.fetch(video_id, languages=['en'])
        snippets = fetched_transcript.snippets

        full_transcript_text = ""
        snippets_list = []

        for snippet in snippets:
            full_transcript_text += snippet.text + " "
            snippets_list.append({
                "text": snippet.text,
                "start": snippet.start,
                "duration": snippet.duration
            })

        transcript = full_transcript_text.strip()

        if not transcript:
            return False, {"error": "Transcript was found but empty.", "code": 500}

        return True, (transcript, snippets_list)

    except Exception as e:
        error_msg = str(e).lower()
        if 'transcript' in error_msg and 'disabled' in error_msg:
            return False, {"error": "Transcripts are disabled for this video.", "code": 403}
        elif 'no transcript' in error_msg:
            return False, {"error": "No transcript available for this video.", "code": 404}
        elif 'video unavailable' in error_msg:
            return False, {"error": "Video is unavailable or does not exist.", "code": 404}
        else:
            return False, {"error": f"Error fetching transcript: {str(e)}", "code": 500}

@app.route('/explain', methods=['POST'])
def explain():
    data = request.json
    video_id = data.get('youtube_id')
    start_time_str = data.get('start_time')
    end_time_str = data.get('end_time')

    GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

    if not video_id:
        return jsonify({"error": "No 'youtube_id' provided"}), 400
    if start_time_str is None or end_time_str is None:
        return jsonify({"error": "Missing start_time or end_time"}), 400

    try:
        start_time = float(start_time_str)
        end_time = float(end_time_str)
    except ValueError:
        return jsonify({"error": "'start_time' and 'end_time' must be numbers"}), 400

    if not GROQ_API_KEY:
        print("Error: GROQ_API_KEY not set.")
        return jsonify({"error": "Backend missing GROQ_API_KEY"}), 500

    print(f"\n--- New Request ---\nVideo: {video_id}, Start: {start_time}, End: {end_time}")

    success, result = get_youtube_transcript(video_id)
    if not success:
        print(f"Transcript fetch failed: {result['error']}")
        return jsonify({"error": result['error']}), result['code']

    all_transcript_text, all_snippets = result

    filtered_snippets = []
    filtered_text_builder = []
    for snippet in all_snippets:
        snippet_start = snippet['start']
        snippet_end = snippet_start + snippet['duration']
        if snippet_start < end_time and snippet_end > start_time:
            filtered_snippets.append(snippet)
            filtered_text_builder.append(snippet['text'])

    filtered_full_text = " ".join(filtered_text_builder).strip()
    if not filtered_full_text:
        print("No transcript found in specified range.")
        return jsonify([])

    print("--- Filtered Transcript (first 500 chars) ---")
    print(filtered_full_text[:500])
    print("---------------------------------------------")

    inputs = {
        "transcript_text": filtered_full_text,
        "transcript_snippets": filtered_snippets
    }
    final_state = app_agent.invoke(inputs)
    explanations = final_state.get("explanations", [])

    print(f"Sending explanations: {json.dumps(explanations, indent=2)}")
    return jsonify(explanations)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok", "message": "Server is running"}), 200

if __name__ == '__main__':
    print("Starting Flask server on http://127.0.0.1:5000")
    print("Ensure GROQ_API_KEY environment variable is set.")
    app.run(debug=True, port=5000)
