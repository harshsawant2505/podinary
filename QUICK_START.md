# Quick Start Guide

Get your Vocab Teacher extension running in 5 minutes!

## Step 1: Load the Extension

1. Open Chrome and go to `chrome://extensions/`
2. Enable **Developer mode** (toggle in top-right corner)
3. Click **"Load unpacked"**
4. Select the `podinary` folder
5. ✅ Extension loaded!

## Step 2: Verify Installation

1. Go to YouTube.com
2. Open any video **that has captions/subtitles**
3. Press `F12` to open Developer Tools
4. Go to the **Console** tab
5. You should see:
   ```
   Vocab Teacher: Initializing...
   Vocab Teacher: New video detected: [VIDEO_ID]
   Vocab Teacher: Fetching transcript for: [VIDEO_ID]
   ```

## Step 3: Test with Demo Data

If your API isn't set up yet, the extension will use demo data:

1. Play any YouTube video
2. Look at the console - you'll see:
   ```
   Vocab Teacher: Using demo data
   ```
3. At 10s, 25s, and 45s, vocab cards will appear! 🎉

## Step 4: Connect Your API

### Your API Endpoint
The extension is already configured to use:
```
http://127.0.0.1:5000/explain
```

### API Expected Format

**Request your API receives:**
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

**Note:** Chunks are limited to 4 minutes OR 5000 characters, whichever comes first.

**Response your API should return:**
```json
[
  {
    "term": "peripatetic",
    "explanation": "Walking from place to place; traveling on foot. Often refers to Aristotle's philosophical school.",
    "timestamp": 5.0
  }
]
```

### Simple Test API (Python)

Create `test_api.py`:

```python
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.post('/explain')
def explain():
    data = request.get_json()
    transcript_text = data.get('transcript_text', '')
    transcript_snippets = data.get('transcript_snippets', [])
    
    print(f"Received transcript: {transcript_text[:100]}...")
    print(f"Number of snippets: {len(transcript_snippets)}")
    
    # Return mock data for testing
    first_snippet = transcript_snippets[0] if transcript_snippets else {'start': 0}
    
    return jsonify([
        {
            'term': 'test word',
            'explanation': f'This is from a transcript chunk with {len(transcript_snippets)} snippets',
            'timestamp': first_snippet['start'] + 2
        }
    ])

if __name__ == '__main__':
    app.run(port=5000, debug=True)
```

Run it:
```bash
pip install flask flask-cors
python test_api.py
```

## Step 5: Test End-to-End

1. Make sure your API is running on `http://127.0.0.1:5000`
2. Open a YouTube video **with captions enabled**
3. The extension will:
   - Fetch the transcript
   - Send first 4 minutes to your API
   - Display vocab cards at specified timestamps
   - Send next chunk after 4 minutes

## Troubleshooting

### ❌ "Transcript not available"
**Solution**: Make sure the video has captions/subtitles. Try videos from official channels which usually have captions.

### ❌ "API request failed"
**Solution**: 
1. Check your API is running: `curl http://127.0.0.1:5000/explain`
2. Check CORS is enabled on your API
3. Look at browser console for detailed error

### ❌ No vocab cards appearing
**Solution**:
1. Check console for errors
2. Verify timestamps in API response match video time
3. Make sure you're watching the video (not paused)

### ❌ Cards not stacking properly
**Solution**: Reload the extension (go to `chrome://extensions/` and click refresh icon)

## Console Commands for Testing

Open the console (`F12`) and try:

```javascript
// Check current transcript data
console.log('Transcript entries:', fullTranscript.length);

// Check current vocab data
console.log('Vocab items:', vocabData);

// Check current video time
console.log('Current time:', document.querySelector('video').currentTime);
```

## Tips

- 🎬 **Best Videos**: Educational content usually has good transcripts
- 📊 **Testing**: Start with short videos (< 5 minutes) for quick testing
- 🔄 **Refresh**: After code changes, click refresh on `chrome://extensions/`
- 🐛 **Debug**: Keep console open to see what's happening
- ⏱️ **Timing**: Cards appear 1 second before the timestamp

## What Happens Every 4 Minutes?

```
Video starts (0:00)
  ↓
Fetch transcript ✓
  ↓
Send chunk 1 (0:00-4:00) to API ✓
  ↓
Display vocab cards as video plays ✓
  ↓
At 4:00 - Send chunk 2 (4:00-8:00) to API ✓
  ↓
Display new vocab cards ✓
  ↓
At 8:00 - Send chunk 3 (8:00-12:00) to API ✓
  ↓
... continues until video ends
```

## Need Help?

Check the console logs - they explain everything the extension is doing:
- When transcript is fetched
- When API requests are made
- When vocab cards are shown
- Any errors that occur

Happy learning! 📚✨

