# Changelog

## Version 1.1.0 - Transcript-Based Processing

### Major Changes

#### 🔄 Transcript Fetching
- **NEW**: Extension now fetches YouTube transcripts automatically using YouTube's Timedtext API
- **NEW**: Supports both JSON3 and XML transcript formats
- **NEW**: Fallback mechanisms for different transcript availability scenarios

#### ⚡ Chunked Processing
- **NEW**: Transcripts are sent to API in 4-minute chunks to prevent rate limiting
- **NEW**: First chunk (0-4 minutes) is sent immediately when video starts
- **NEW**: Subsequent chunks sent automatically every 4 minutes
- **NEW**: Intelligent chunk management with automatic cleanup on video change

#### 📡 API Changes
- **BREAKING**: API endpoint now receives transcript data instead of `youtube_id`
- **NEW**: Request format:
  ```json
  {
    "transcript": "transcript text...",
    "start_time": 0,
    "end_time": 240
  }
  ```
- **REMOVED**: `youtube_id` is no longer sent to the API

#### 🎨 UI Improvements
- **NEW**: Vocabulary cards persist until manually closed (no auto-dismiss)
- **NEW**: Cards stack naturally below each other
- **NEW**: Scrollable container for multiple vocabulary cards
- **NEW**: Custom scrollbar styling with gradient theme

#### 🔧 Technical Improvements
- **NEW**: Vocabulary data accumulates from multiple API requests
- **NEW**: Monitoring starts automatically after first chunk is processed
- **NEW**: Better cleanup when switching between videos
- **NEW**: All transcript chunks are cleared on video change

### Files Modified

1. **content.js**
   - Added transcript fetching logic
   - Implemented chunked processing system
   - Updated API request format
   - Removed auto-close timer from popups

2. **popup.css**
   - Made container scrollable
   - Added custom scrollbar styling
   - Removed fixed positioning for stacked cards
   - Improved responsive design

3. **manifest.json**
   - Added localhost API permissions
   - Removed icon references

4. **README.md**
   - Updated API specification
   - Updated features list
   - Updated "How It Works" section

5. **API_EXAMPLE.md**
   - Updated all code examples (Node.js, Flask, FastAPI)
   - Added LLM integration examples
   - Updated testing examples
   - Updated caching strategies

### Migration Guide

If you're upgrading from a previous version:

1. **Update Your API Endpoint**: Your API must now accept transcript data:
   ```json
   {
     "transcript": "text...",
     "start_time": 0,
     "end_time": 240
   }
   ```

2. **Update Response Format**: Ensure timestamps in your response fall within the chunk's time range

3. **Reload Extension**: After updating, reload the extension in Chrome

4. **Test**: Visit a YouTube video with captions/transcripts available

### Known Limitations

- Only works with videos that have transcripts/captions available
- Currently only fetches English transcripts (can be modified for other languages)
- Requires videos to have auto-generated or manual captions enabled

### Future Enhancements

- [ ] Support for multiple language transcripts
- [ ] User-configurable chunk duration
- [ ] Retry logic for failed API requests
- [ ] Transcript preview in popup
- [ ] Download vocabulary list feature

