# API Implementation Example

This document provides example implementations for the backend API that your Chrome extension will communicate with.

## API Specification

**Endpoint:** Your choice (update in `content.js`)  
**Method:** POST  
**Content-Type:** application/json

### Request Format

The extension sends transcript data in chunks (4 minutes OR 5000 characters max):

```json
{
  "transcript_text": "This video discusses several advanced topics. First, we'll examine the peripatetic nature of early philosophers. Then, we will look at how to not obfuscate your code, which is a common problem. Finally, we'll touch on the quintessential elements of good design. We will also discuss ephemeral art forms.",
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
    },
    {
      "text": "Then, we will look at how to not obfuscate your code, which is a common problem.",
      "start": 9.0,
      "duration": 6.1
    },
    {
      "text": "Finally, we'll touch on the quintessential elements of good design.",
      "start": 15.5,
      "duration": 4.5
    },
    {
      "text": "We will also discuss ephemeral art forms.",
      "start": 20.2,
      "duration": 3.0
    }
  ]
}
```

**Request Fields:**
- `transcript_text` (string): The combined transcript text for this chunk (max 5000 characters)
- `transcript_snippets` (array): Individual transcript segments with precise timing
  - `text` (string): The text for this segment
  - `start` (number): Start time in seconds
  - `duration` (number): Duration in seconds

### Response Format

```json
[
  {
    "term": "multicultural",
    "explanation": "Composed of people from different cultures, often living together in a single community.",
    "timestamp": 45.66
  },
  {
    "term": "perseverance",
    "explanation": "Persistence in doing something despite difficulty or delay in achieving success.",
    "timestamp": 120.5
  }
]
```

## Example Implementation (Node.js/Express)

```javascript
const express = require('express');
const cors = require('cors');
const app = express();

// Enable CORS for YouTube
app.use(cors({
  origin: 'https://www.youtube.com',
  methods: ['POST', 'OPTIONS'],
  allowedHeaders: ['Content-Type']
}));

app.use(express.json());

// Vocabulary endpoint
app.post('/api/vocab', async (req, res) => {
  const { transcript_text, transcript_snippets } = req.body;
  
  if (!transcript_text || !transcript_snippets) {
    return res.status(400).json({ error: 'transcript_text and transcript_snippets are required' });
  }
  
  try {
    // Here you would call your LLM to analyze the transcript
    // Example with OpenAI:
    /*
    const completion = await openai.chat.completions.create({
      model: "gpt-3.5-turbo",
      messages: [{
        role: "system",
        content: "You are a vocabulary teacher. Extract difficult or educational words from the transcript and provide explanations with accurate timestamps."
      }, {
        role: "user",
        content: `Analyze this transcript and identify challenging vocabulary:\n\n${transcript_text}\n\nTimestamps available: ${transcript_snippets.map(s => `${s.start}s: "${s.text}"`).join('\n')}`
      }]
    });
    
    const vocabData = JSON.parse(completion.choices[0].message.content);
    */
    
    // Mock response for demonstration
    const firstSnippet = transcript_snippets[0];
    const vocabData = [
      {
        term: 'example word',
        explanation: 'An educational explanation of the word',
        timestamp: firstSnippet.start + 1 // timestamp within the chunk
      }
    ];
    
    res.json(vocabData);
  } catch (error) {
    console.error('Error processing transcript:', error);
    res.status(500).json({ error: 'Failed to process transcript' });
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Vocab API running on port ${PORT}`);
});
```

## Example Implementation (Python/Flask)

```python
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)

# Enable CORS for YouTube
CORS(app, origins=['https://www.youtube.com'])

@app.route('/api/vocab', methods=['POST'])
def get_vocab():
    data = request.get_json()
    
    if not data or 'transcript_text' not in data or 'transcript_snippets' not in data:
        return jsonify({'error': 'transcript_text and transcript_snippets are required'}), 400
    
    transcript_text = data['transcript_text']
    transcript_snippets = data['transcript_snippets']
    
    try:
        # Here you would call your LLM to analyze the transcript
        # Example with OpenAI:
        """
        from openai import OpenAI
        client = OpenAI()
        
        # Build timestamp info for context
        timestamp_info = '\n'.join([
            f"{snippet['start']}s: \"{snippet['text']}\""
            for snippet in transcript_snippets
        ])
        
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{
                "role": "system",
                "content": "You are a vocabulary teacher. Extract difficult or educational words from the transcript and provide explanations with accurate timestamps."
            }, {
                "role": "user",
                "content": f"Analyze this transcript and identify challenging vocabulary:\n\n{transcript_text}\n\nTimestamps available:\n{timestamp_info}"
            }]
        )
        
        vocab_data = json.loads(completion.choices[0].message.content)
        """
        
        # Mock response for demonstration
        first_snippet = transcript_snippets[0] if transcript_snippets else {'start': 0}
        vocab_data = [
            {
                'term': 'example word',
                'explanation': 'An educational explanation of the word',
                'timestamp': first_snippet['start'] + 1
            }
        ]
        
        return jsonify(vocab_data)
    except Exception as e:
        print(f'Error processing transcript: {e}')
        return jsonify({'error': 'Failed to process transcript'}), 500

if __name__ == '__main__':
    app.run(port=3000, debug=True)
```

## Example Implementation (Python/FastAPI)

```python
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

app = FastAPI()

# Enable CORS for YouTube
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://www.youtube.com"],
    allow_methods=["POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)

# Models
class TranscriptSnippet(BaseModel):
    text: str
    start: float
    duration: float

class VocabRequest(BaseModel):
    transcript_text: str
    transcript_snippets: List[TranscriptSnippet]

class VocabItem(BaseModel):
    term: str
    explanation: str
    timestamp: float

@app.post('/api/vocab', response_model=List[VocabItem])
async def get_vocab(request: VocabRequest):
    try:
        # Here you would call your LLM to analyze the transcript
        # Example with OpenAI:
        """
        from openai import AsyncOpenAI
        client = AsyncOpenAI()
        
        # Build timestamp info for context
        timestamp_info = '\n'.join([
            f"{snippet.start}s: \"{snippet.text}\""
            for snippet in request.transcript_snippets
        ])
        
        completion = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{
                "role": "system",
                "content": "You are a vocabulary teacher. Extract difficult or educational words from the transcript and provide explanations with accurate timestamps."
            }, {
                "role": "user",
                "content": f"Analyze this transcript and identify challenging vocabulary:\n\n{request.transcript_text}\n\nTimestamps available:\n{timestamp_info}"
            }]
        )
        
        vocab_data = json.loads(completion.choices[0].message.content)
        return [VocabItem(**item) for item in vocab_data]
        """
        
        # Mock response for demonstration
        first_snippet = request.transcript_snippets[0] if request.transcript_snippets else None
        timestamp = first_snippet.start + 1 if first_snippet else 0
        
        return [
            VocabItem(
                term='example word',
                explanation='An educational explanation of the word',
                timestamp=timestamp
            )
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process transcript: {str(e)}")
```

## Real-World Implementation Tips

### 1. Database Storage
Instead of hardcoded dictionaries, use a database:

```sql
CREATE TABLE vocabulary (
    id SERIAL PRIMARY KEY,
    youtube_id VARCHAR(20) NOT NULL,
    term VARCHAR(100) NOT NULL,
    explanation TEXT NOT NULL,
    timestamp DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_youtube_id (youtube_id)
);
```

### 2. AI-Powered Vocabulary Extraction
Use LLMs to automatically extract and explain vocabulary:

```python
from openai import OpenAI
import json

def extract_vocabulary(transcript, start_time, end_time):
    client = OpenAI()
    
    prompt = f"""Analyze this transcript segment from {start_time} to {end_time} seconds.
    Extract 3-5 educational or difficult vocabulary terms that would benefit language learners.
    For each term, provide:
    1. The exact term as it appears
    2. A clear, concise explanation
    3. An estimated timestamp (between {start_time} and {end_time})
    
    Return as JSON array with format: [{{"term": "...", "explanation": "...", "timestamp": 123.45}}]
    
    Transcript: {transcript}"""
    
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{
            "role": "system",
            "content": "You are a vocabulary teacher helping students learn from video content."
        }, {
            "role": "user",
            "content": prompt
        }],
        response_format={ "type": "json_object" }
    )
    
    result = json.loads(completion.choices[0].message.content)
    return result.get('vocabulary', [])
```

### 3. Caching
Implement caching to avoid repeated processing:

```javascript
const crypto = require('crypto');
const cache = new Map();

app.post('/api/vocab', async (req, res) => {
  const { transcript, start_time, end_time } = req.body;
  
  // Create cache key from transcript hash and time range
  const cacheKey = crypto
    .createHash('md5')
    .update(`${transcript}-${start_time}-${end_time}`)
    .digest('hex');
  
  // Check cache first
  if (cache.has(cacheKey)) {
    console.log('Cache hit!');
    return res.json(cache.get(cacheKey));
  }
  
  // Generate vocab data using LLM
  const vocabData = await generateVocabData(transcript, start_time, end_time);
  
  // Store in cache
  cache.set(cacheKey, vocabData);
  
  res.json(vocabData);
});
```

### 4. Rate Limiting
Protect your API from abuse:

```javascript
const rateLimit = require('express-rate-limit');

const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100 // limit each IP to 100 requests per windowMs
});

app.use('/api/', limiter);
```

## Testing Your API

### Using curl:
```bash
curl -X POST http://localhost:3000/api/vocab \
  -H "Content-Type: application/json" \
  -d '{
    "transcript_text": "This video discusses several advanced topics. First, we will examine the peripatetic nature of early philosophers. Then, we will look at how to not obfuscate your code.",
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
      },
      {
        "text": "Then, we will look at how to not obfuscate your code.",
        "start": 9.0,
        "duration": 6.1
      }
    ]
  }'
```

### Using JavaScript (Browser Console):
```javascript
fetch('http://localhost:3000/api/vocab', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ 
    transcript_text: 'This video discusses several advanced topics. First, we will examine the peripatetic nature of early philosophers.',
    transcript_snippets: [
      { text: 'This video discusses several advanced topics.', start: 0.5, duration: 3.0 },
      { text: 'First, we will examine the peripatetic nature of early philosophers.', start: 3.5, duration: 5.2 }
    ]
  })
})
.then(r => r.json())
.then(data => console.log(data));
```

### Using Postman:
1. Method: POST
2. URL: `http://localhost:3000/api/vocab`
3. Headers: `Content-Type: application/json`
4. Body (raw JSON):
```json
{
  "transcript_text": "This video discusses several advanced topics. First, we will examine the peripatetic nature of early philosophers. Then, we will look at how to not obfuscate your code.",
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
    },
    {
      "text": "Then, we will look at how to not obfuscate your code.",
      "start": 9.0,
      "duration": 6.1
    }
  ]
}
```

## Deployment

### Popular Options:
- **Vercel** (Node.js/Next.js)
- **Railway** (Any language)
- **Heroku** (Any language)
- **AWS Lambda** (Serverless)
- **Google Cloud Run** (Containerized)

Don't forget to:
1. Set environment variables
2. Configure CORS for production domain
3. Set up SSL/HTTPS
4. Implement authentication if needed

## Integration with Chrome Extension

Once your API is deployed, update `content.js`:

```javascript
const API_ENDPOINT = 'https://your-api.com/api/vocab';
```

That's it! Your Chrome extension will now fetch real vocabulary data from your API.

