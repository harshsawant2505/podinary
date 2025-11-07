# Update Summary - Enhanced API Request Format

## What Changed?

The API request format has been updated to provide more detailed transcript data with precise timing information for each segment.

## New API Request Format

### Before (Old Format):
```json
{
  "transcript": "combined text...",
  "start_time": 0,
  "end_time": 240
}
```

### After (New Format):
```json
{
  "transcript_text": "This video discusses several advanced topics. First, we'll examine the peripatetic nature...",
  "transcript_snippets": [
    {
      "text": "This video discusses several advanced topics.",
      "start": 0.5,
      "duration": 3.0
    },
    {
      "text": "First, we'll examine the peripatetic nature of early philosophers.",
      "start": 3.5,
      "duration": 5.2
    }
  ]
}
```

## Key Improvements

### 1. Detailed Timing Information
- Each transcript segment now includes its exact `start` time and `duration`
- This allows your LLM to provide more accurate timestamps for vocabulary terms
- The LLM can map words to specific time ranges

### 2. Character Limit Protection
- Chunks are now limited to **4 minutes OR 5000 characters**, whichever comes first
- This prevents API overload and respects token limits
- Console logs show both time range AND character count for each chunk

### 3. Better Context for LLM
Your API can now:
- See the full combined text in `transcript_text`
- Access individual timed segments in `transcript_snippets`
- Provide more accurate timestamps based on segment boundaries
- Better understand which words appear when in the video

## Example Usage in Your API

### Python/Flask:
```python
@app.post('/explain')
def explain():
    data = request.get_json()
    transcript_text = data.get('transcript_text', '')
    transcript_snippets = data.get('transcript_snippets', [])
    
    # Use transcript_text for full context
    # Use transcript_snippets for precise timing
    
    # Example: Find which snippet contains a word
    for snippet in transcript_snippets:
        if 'peripatetic' in snippet['text'].lower():
            timestamp = snippet['start'] + 1  # Word appears around this time
            break
    
    return jsonify([{
        'term': 'peripatetic',
        'explanation': 'Walking from place to place...',
        'timestamp': timestamp
    }])
```

### With OpenAI:
```python
# Build context with timestamps
timestamp_context = '\n'.join([
    f"{s['start']}s ({s['duration']}s): \"{s['text']}\""
    for s in transcript_snippets
])

prompt = f"""
Analyze this transcript and extract vocabulary terms with timestamps:

Full text:
{transcript_text}

Timestamp breakdown:
{timestamp_context}

Return JSON array with term, explanation, and accurate timestamp.
"""
```

## Console Output Example

When running, you'll see:
```
Vocab Teacher: Sending chunk 1 (0s - 238.5s, 4823 chars)
Vocab Teacher: Sending chunk 2 (240s - 478.2s, 4956 chars)
```

This shows:
- Chunk number
- Time range covered
- Character count (always ≤ 5000)

## Migration Checklist

- [x] Update content.js with new chunking logic
- [x] Add MAX_CHARS constant (5000)
- [x] Build transcript_text from combined segments
- [x] Build transcript_snippets array with text/start/duration
- [x] Update README.md with new API spec
- [x] Update API_EXAMPLE.md with all examples (Node.js, Flask, FastAPI)
- [x] Update QUICK_START.md with new format
- [x] Update test examples with new format

## Testing Your API

Use this test payload:

```bash
curl -X POST http://127.0.0.1:5000/explain \
  -H "Content-Type: application/json" \
  -d '{
    "transcript_text": "This video discusses several advanced topics. First, we will examine the peripatetic nature of early philosophers.",
    "transcript_snippets": [
      {
        "text": "This video discusses several advanced topics.",
        "start": 0.5,
        "duration": 3.0
      },
      {
        "text": "First, we will examine the peripatetic nature of early philosophers.",
        "start": 3.5,
        "duration": 5.2
      }
    ]
  }'
```

Expected response:
```json
[
  {
    "term": "peripatetic",
    "explanation": "Walking from place to place; traveling on foot.",
    "timestamp": 5.0
  }
]
```

## Benefits for Your LLM

1. **Better Accuracy**: LLM can see exactly when each phrase occurs
2. **Context Awareness**: Full text + segmented view = better understanding
3. **Precise Timestamps**: Return timestamps that match actual word occurrences
4. **Scalability**: 5000 char limit prevents token overflow
5. **Flexibility**: Can analyze individual segments or full text

## What Stays the Same

- Response format (unchanged)
- 4-minute interval timing
- Vocabulary card UI
- Extension behavior

## Need Help?

Check the console logs - they'll show:
- Chunk size in both time and characters
- When chunks are sent
- What data structure is being sent

The extension is now optimized for LLM processing with detailed timing data! 🚀

