// Vocab Teacher Content Script
let vocabData = [];
let currentVideoId = null;
let checkInterval = null;
let popupContainer = null;
let requestedChunks = new Set(); // Track which chunks we've already requested
let pendingRequests = new Map(); // Track chunks currently being fetched (chunkIndex -> Promise)

// API Configuration - Update this with your actual API endpoint
const API_ENDPOINT = 'http://127.0.0.1:5000/explain';
const CHUNK_DURATION = 120; // 4 minutes in seconds
const EARLY_REQUEST_TIME = 20; // Send request 20 seconds before chunk starts

// Initialize the extension
function init() {
  console.log('Vocab Teacher: Initializing...');
  createPopupContainer();
  observeVideoChanges();
  checkForVideo();
}

// Create the popup container
function createPopupContainer() {
  if (popupContainer) return;
  
  popupContainer = document.createElement('div');
  popupContainer.id = 'vocab-teacher-container';
  document.body.appendChild(popupContainer);
}

// Observe URL changes (YouTube is a SPA)
function observeVideoChanges() {
  let lastUrl = location.href;
  
  new MutationObserver(() => {
    const url = location.href;
    if (url !== lastUrl) {
      lastUrl = url;
      checkForVideo();
    }
  }).observe(document.body, { childList: true, subtree: true });
}

// Check if we're on a video page
function checkForVideo() {
  const urlParams = new URLSearchParams(window.location.search);
  const videoId = urlParams.get('v');
  
  if (videoId && videoId !== currentVideoId) {
    currentVideoId = videoId;
    console.log('Vocab Teacher: New video detected:', videoId);
    clearScheduledPopups();
    fetchVocabData(videoId);
  } else if (!videoId) {
    currentVideoId = null;
    clearScheduledPopups();
  }
}

// Clear all data when switching videos
function clearScheduledPopups() {
  vocabData = [];
  requestedChunks.clear();
  pendingRequests.clear();
  
  // Clear monitoring interval
  if (checkInterval) {
    clearInterval(checkInterval);
    checkInterval = null;
  }
  
  // Clear all visible popups when switching videos
  if (popupContainer) {
    popupContainer.innerHTML = '';
  }
}

// Send chunk request to API via background script
async function sendChunkRequest(videoId, chunkIndex) {
  // If this chunk is already being fetched, return the existing promise
  if (pendingRequests.has(chunkIndex)) {
    console.log(`Vocab Teacher: Chunk ${chunkIndex + 1} is already being fetched, skipping duplicate request`);
    return pendingRequests.get(chunkIndex);
  }
  
  // If we've already successfully fetched this chunk, skip it
  if (requestedChunks.has(chunkIndex)) {
    console.log(`Vocab Teacher: Chunk ${chunkIndex + 1} already fetched, skipping`);
    return;
  }
  
  const startTime = chunkIndex * CHUNK_DURATION;
  const endTime = startTime + CHUNK_DURATION;
  
  console.log(`Vocab Teacher: Requesting chunk ${chunkIndex + 1} (${startTime}s - ${endTime}s) for video ${videoId}`);
  
  // Create the fetch promise
  const fetchPromise = (async () => {
    try {
      // Send message to background script to handle the fetch
      const response = await chrome.runtime.sendMessage({
        action: 'fetchVocab',
        data: {
          apiEndpoint: API_ENDPOINT,
          videoId: videoId,
          startTime: startTime,
          endTime: endTime
        }
      });
      
      if (!response.success) {
        throw new Error(response.error || 'API request failed');
      }
      
      const newVocabData = response.data;
      console.log('Vocab Teacher: Received vocab data:', newVocabData);
      
      // Add new vocab data to existing data
      vocabData = [...vocabData, ...newVocabData];
      
      // Mark as successfully fetched
      requestedChunks.add(chunkIndex);
      
    } catch (error) {
      console.error('Vocab Teacher: Error sending chunk request:', error);
    } finally {
      // Remove from pending requests when done (success or failure)
      pendingRequests.delete(chunkIndex);
    }
  })();
  
  // Track this pending request
  pendingRequests.set(chunkIndex, fetchPromise);
  
  return fetchPromise;
}

// Check if we need to request any chunks based on current video time
function checkAndRequestChunks(videoId, currentTime) {
  // Calculate which chunk the current time falls into
  const currentChunkIndex = Math.floor(currentTime / CHUNK_DURATION);
  
  // Request the current chunk (sendChunkRequest will handle duplicate prevention)
  sendChunkRequest(videoId, currentChunkIndex);
  
  // Optionally preload the next chunk if we're close to it (within EARLY_REQUEST_TIME seconds)
  const timeIntoChunk = currentTime % CHUNK_DURATION;
  const nextChunkIndex = currentChunkIndex + 1;
  
  if (timeIntoChunk >= (CHUNK_DURATION - EARLY_REQUEST_TIME)) {
    sendChunkRequest(videoId, nextChunkIndex);
  }
}

// Start monitoring video time and fetching vocab data
function fetchVocabData(videoId) {
  console.log('Vocab Teacher: Starting vocab monitoring for video:', videoId);
  
  // Start time monitoring which will trigger chunk requests
  startTimeMonitoring(videoId);
}

// Use demo data for testing
function useDemoData() {
  console.log('%c📚 Vocab Teacher: Using demo data for testing', 'color: #667eea; font-weight: bold; font-size: 14px');
  console.log('%cDemo vocab cards will appear at 10s, 25s, and 45s in this video', 'color: #888; font-style: italic');
  console.log('%c💡 Note: API-based vocab fetching will work once your backend is ready', 'color: #4caf50; font-weight: bold');
  
  vocabData = [
    {
      "explanation": "Composed of people from different cultures, often living together in a single community.",
      "term": "multicultural",
      "timestamp": 10,
      "synonyms": ["diverse", "cosmopolitan", "multiethnic"]
    },
    {
      "explanation": "The action of keeping something harmful under control or within limits.",
      "term": "containment",
      "timestamp": 25,
      "synonyms": ["control", "restraint", "limitation"]
    },
    {
      "explanation": "A remarkable concurrence of events or circumstances without apparent causal connection.",
      "term": "coincidence",
      "timestamp": 45,
      "synonyms": ["chance", "accident", "fluke", "serendipity"]
    }
  ];
  startTimeMonitoring(currentVideoId || 'demo');
}

// Monitor video playback time
function startTimeMonitoring(videoId) {
  if (checkInterval) {
    clearInterval(checkInterval);
  }
  
  // Check every 1 second for chunk requests and every 100ms for popups
  let lastCheckTime = -1;
  
  checkInterval = setInterval(() => {
    const video = document.querySelector('video');
    if (!video) return;
    
    const currentTime = video.currentTime;
    
    // Check for chunk requests every second (not every 100ms to avoid spam)
    const currentSecond = Math.floor(currentTime);
    if (currentSecond !== lastCheckTime) {
      lastCheckTime = currentSecond;
      checkAndRequestChunks(videoId, currentTime);
    }
    
    // Check if we need to show any popups
    vocabData.forEach((item, index) => {
      const showTime = item.timestamp; // Show 1 second before
      
      // Show popup if we're within 200ms of the show time and haven't shown it yet
      if (!item.shown && currentTime >= showTime && currentTime < showTime + 0.2) {
        item.shown = true;
        showVocabPopup(item);
      }
    });
    
    // Reset shown flags if user seeks backward
    vocabData.forEach(item => {
      if (item.shown && currentTime < item.timestamp - 1) {
        item.shown = false;
      }
    });
    
  }, 100);
}

// Show vocabulary popup
function showVocabPopup(vocabItem) {
  console.log('Vocab Teacher: Showing popup for:', vocabItem.term);
  
  // Create popup element
  const popup = document.createElement('div');
  popup.className = 'vocab-popup';
  // Build synonyms HTML if available
  const synonymsHtml = vocabItem.synonyms && vocabItem.synonyms.length > 0
    ? `<div class="vocab-synonyms">
         <span class="synonyms-label">Synonyms:</span>
         <span class="synonyms-list">${vocabItem.synonyms.join(', ')}</span>
       </div>`
    : '';
  
  popup.innerHTML = `
    <div class="vocab-popup-content">
      <div class="vocab-icon">📚</div>
      <div class="vocab-content-wrapper">
        <div class="vocab-term">${vocabItem.term}</div>
        <div class="vocab-explanation">${vocabItem.explanation}</div>
        ${synonymsHtml}
      </div>
      <div class="vocab-timestamp">⏱️ ${formatTimestamp(vocabItem.timestamp)}</div>
      <button class="vocab-close">&times;</button>
    </div>
  `;
  
  // Add to container (prepend to show newest at top)
  popupContainer.insertBefore(popup, popupContainer.firstChild);
  
  // Animate in
  setTimeout(() => popup.classList.add('show'), 10);
  
  // Add close button functionality
  const closeBtn = popup.querySelector('.vocab-close');
  closeBtn.addEventListener('click', () => {
    closePopup(popup);
  });
}

// Close popup with animation
function closePopup(popup) {
  popup.classList.remove('show');
  popup.classList.add('hide');
  
  setTimeout(() => {
    if (popup.parentElement) {
      popup.remove();
    }
  }, 300);
}

// Format timestamp for display
function formatTimestamp(seconds) {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs.toString().padStart(2, '0')}`;
}

// Clean up when navigating away (use visibilitychange instead of beforeunload)
document.addEventListener('visibilitychange', () => {
  if (document.hidden) {
    // Page is hidden, pause operations if needed
    // Don't clear everything as user might come back
  }
});

// Start the extension
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}

