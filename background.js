// Background Service Worker for Vocab Teacher
// This handles API requests to avoid CORS issues with content scripts

console.log('Vocab Teacher: Background service worker loaded');

// Listen for messages from content script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'fetchVocab') {
    // Handle vocab fetch request
    handleVocabFetch(request.data)
      .then(data => {
        sendResponse({ success: true, data: data });
      })
      .catch(error => {
        console.error('Vocab Teacher: Background fetch error:', error);
        sendResponse({ success: false, error: error.message });
      });
    
    // Return true to indicate we'll send response asynchronously
    return true;
  }
});

// Fetch vocab data from API
async function handleVocabFetch({ apiEndpoint, videoId, startTime, endTime }) {
  console.log(`Vocab Teacher: Background fetching chunk (${startTime}s - ${endTime}s) for video ${videoId}`);
  
  try {
    const response = await fetch(apiEndpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ 
        youtube_id: videoId,
        start_time: startTime,
        end_time: endTime
      })
    });
    
    if (!response.ok) {
      throw new Error(`API request failed with status: ${response.status}`);
    }
    
    const data = await response.json();
    console.log('Vocab Teacher: Background received vocab data:', data);
    
    return data;
    
  } catch (error) {
    console.error('Vocab Teacher: Background fetch error:', error);
    throw error;
  }
}

