# Installation Guide

## Quick Start

### Step 1: Configure Your API Endpoint

Before installing the extension, open `content.js` and update line 9:

```javascript
const API_ENDPOINT = 'YOUR_API_ENDPOINT_HERE';
```

Replace with your actual API endpoint, for example:
```javascript
const API_ENDPOINT = 'https://api.example.com/vocab';
```

### Step 2: Generate Icons (Optional)

The extension includes an SVG icon. To generate PNG icons:

**Option A - Using Online Converter:**
1. Open `icon.svg` in any SVG to PNG converter
2. Export as:
   - `icon16.png` (16x16 pixels)
   - `icon48.png` (48x48 pixels)
   - `icon128.png` (128x128 pixels)

**Option B - Skip Icons:**
You can also remove the icons section from `manifest.json`:
```json
Remove or comment out:
"icons": {
  "16": "icon16.png",
  "48": "icon48.png",
  "128": "icon128.png"
}
```

### Step 3: Load Extension in Chrome

1. Open Chrome browser
2. Navigate to `chrome://extensions/`
3. Enable **Developer mode** (toggle switch in top-right)
4. Click **"Load unpacked"**
5. Select the folder containing your extension files
6. ✅ Extension is now installed!

### Step 4: Test the Extension

1. Go to YouTube.com
2. Open any video
3. Open Developer Tools (F12)
4. Check the Console tab - you should see:
   ```
   Vocab Teacher: Initializing...
   Vocab Teacher: New video detected: [VIDEO_ID]
   ```

### Step 5: Verify It Works

**With Demo Data (no API needed):**
- If your API endpoint is not configured or fails, the extension uses demo data
- Popups will appear at 10s, 25s, and 45s in any video

**With Your API:**
- Play a video that your API has vocabulary data for
- Popups should appear 1 second before each timestamp

## Troubleshooting

### "Extensions" page won't load extension
- Make sure all files are in the same folder
- Check that `manifest.json` is valid JSON
- Try reloading the extension

### Console shows "API request failed"
- Verify your API endpoint URL is correct
- Check that your API accepts POST requests
- Ensure CORS is enabled on your API server

### No popups appearing
- Check console for errors
- Verify you're on a video page (not just youtube.com)
- Make sure timestamps in API response are numbers (not strings)

### Popups appear at wrong time
- API timestamps should be in seconds (not milliseconds)
- Verify the video is actually playing

## CORS Configuration

Your API server needs to allow requests from YouTube. Example headers:

```
Access-Control-Allow-Origin: https://www.youtube.com
Access-Control-Allow-Methods: POST, OPTIONS
Access-Control-Allow-Headers: Content-Type
```

## Testing Your API

You can test your API endpoint using curl:

```bash
curl -X POST https://your-api.com/vocab \
  -H "Content-Type: application/json" \
  -d '{"youtube_id": "dQw4w9WgXcQ"}'
```

Expected response:
```json
[
  {
    "term": "example",
    "explanation": "A thing characteristic of its kind.",
    "timestamp": 30.5
  }
]
```

## Next Steps

Once installed and working:
- Visit YouTube and watch videos with vocabulary
- Click the ✕ button to close popups early
- Popups auto-close after 8 seconds
- Seeking backward in video will show popups again

Enjoy learning! 📚

