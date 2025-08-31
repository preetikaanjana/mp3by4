document.addEventListener('DOMContentLoaded', () => {
  const extractBtn = document.getElementById("extractBtn");
  const btnText = document.getElementById("btnText");
  const btnLoading = document.getElementById("btnLoading");
  const resultDiv = document.getElementById("result");

  // Voice selection options
  const voiceOptions = {
    "professional": "🎯 Professional - Clear, authoritative voice",
    "friendly": "😊 Friendly - Warm, approachable tone",
    "energetic": "⚡ Energetic - Dynamic, engaging delivery",
    "sophisticated": "🎭 Sophisticated - Deep, refined voice",
    "google_premium": "🌟 Google Premium - Natural, high-quality"
  };

  function showLoading() {
    btnLoading.style.display = "block";
    btnText.style.display = "none";
    extractBtn.disabled = true;
  }

  function hideLoading() {
    btnLoading.style.display = "none";
    btnText.style.display = "block";
    extractBtn.disabled = false;
  }

  function addStatus(message, type = 'info') {
    const statusDiv = document.createElement('div');
    statusDiv.className = `status ${type}`;
    statusDiv.innerHTML = message;
    resultDiv.appendChild(statusDiv);
  }

  function clearResults() {
    resultDiv.innerHTML = '';
  }

  function createVoiceSelector() {
    const voiceContainer = document.createElement('div');
    voiceContainer.className = 'voice-selector';
    voiceContainer.innerHTML = `
      <h4>🎤 Choose Your Voice Style:</h4>
      <div class="voice-options">
        ${Object.entries(voiceOptions).map(([key, description]) => `
          <label class="voice-option">
            <input type="radio" name="voice" value="${key}" ${key === 'professional' ? 'checked' : ''}>
            <span class="voice-label">${description}</span>
          </label>
        `).join('')}
      </div>
    `;
    return voiceContainer;
  }

  function createIsolationToggle() {
    const toggle = document.createElement('div');
    toggle.className = 'voice-selector';
    toggle.innerHTML = `
      <label class="voice-option">
        <input type="checkbox" id="isolationToggle">
        <span class="voice-label">🪄 Isolate background (requires MediaPipe, slower but cinematic)</span>
      </label>
    `;
    return toggle;
  }

  async function testServerConnection() {
    try {
      const response = await fetch("http://localhost:8080/", {
        method: "GET",
        mode: "cors"
      });
      return response.ok;
    } catch (error) {
      console.error("Server connection test failed:", error);
      return false;
    }
  }

  extractBtn.addEventListener("click", async () => {
    try {
      showLoading();
      clearResults();
      addStatus("🚀 Starting conversion process...", "info");
      addStatus("🔍 Testing server connection...", "info");
      
      const serverConnected = await testServerConnection();
      if (!serverConnected) {
        throw new Error("Cannot connect to server. Make sure it's running on localhost:8080");
      }
      
      addStatus("✅ Server connection successful", "success");
      
      // Add voice selector
      const voiceSelector = createVoiceSelector();
      resultDiv.appendChild(voiceSelector);

      // Add isolation toggle
      const isolationToggle = createIsolationToggle();
      resultDiv.appendChild(isolationToggle);
      
      const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
      const activeTab = tabs[0];
      
      if (!activeTab || !activeTab.url) {
        throw new Error("Could not get current tab URL");
      }
      
      addStatus(`📄 Processing: ${new URL(activeTab.url).hostname}`, "info");
      
      const textResult = await chrome.scripting.executeScript({
        target: { tabId: activeTab.id },
        function: extractText,
      });
      
      addStatus("✅ Text extracted successfully", "success");
      addStatus("🎙️ Generating narration...", "info");
      
      // Get selected voice type
      const selectedVoice = document.querySelector('input[name="voice"]:checked').value;
      const isolation = !!document.getElementById('isolationToggle')?.checked;
      addStatus(`🎤 Using voice: ${voiceOptions[selectedVoice].split(' - ')[1]}` + (isolation ? " • 🪄 Isolation ON" : ""), "info");
      
      const narrationResponse = await fetch("http://localhost:8080/generate_narration", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Accept": "application/json"
        },
        mode: "cors",
        body: JSON.stringify({ 
          url: activeTab.url,
          voice_type: selectedVoice,
          isolation
        }),
      });
      
      if (!narrationResponse.ok) {
        throw new Error(`Narration failed: ${narrationResponse.status} - ${narrationResponse.statusText}`);
      }
      
      const narrationData = await narrationResponse.json();
      
      if (narrationData.status === "demo") {
        addStatus("⚠️ Demo mode: Using sample response", "info");
        addStatus(`📝 Sample narrative: ${narrationData.narrative}`, "info");
        
        const demoContainer = document.createElement('div');
        demoContainer.className = 'media-controls';
        demoContainer.innerHTML = `
          <h4>🎭 Demo Mode</h4>
          <p>This is a demo response. For full functionality:</p>
          <ul>
            <li>✅ Server is running on port 8080</li>
            <li>⚠️ Full MP3by4 server needs to be configured</li>
            <li>💡 Check the Python console for setup instructions</li>
          </ul>
        `;
        resultDiv.appendChild(demoContainer);
        addStatus("🎉 Demo completed! Server is working correctly.", "success");
        addStatus("💡 Next: Configure the full MP3by4 server with Flask", "info");
      } else {
        addStatus("✅ Narration generated successfully", "success");
        addStatus(`📝 Summary: ${narrationData.narrative.substring(0, 200)}...`, "info");
        
        // Display audio player
        if (narrationData.mp3_url) {
          const audioContainer = document.createElement('div');
          audioContainer.className = 'media-controls';
          audioContainer.innerHTML = `
            <h4>🎧 Listen to the narration:</h4>
            <audio controls>
              <source src="http://localhost:8080${narrationData.mp3_url}" type="audio/mpeg">
              Your browser does not support the audio element.
            </audio>
            <p><strong>Voice Type:</strong> ${voiceOptions[narrationData.voice_type]?.split(' - ')[1] || narrationData.voice_type}</p>
          `;
          resultDiv.appendChild(audioContainer);
        }

        // Display video player if available
        if (narrationData.video_url) {
          const videoContainer = document.createElement('div');
          videoContainer.className = 'media-controls';
          
          // Check if it's an HTML video file
          if (narrationData.video_url.endsWith('.html')) {
            videoContainer.innerHTML = `
              <h4>🎬 Generated Video:</h4>
              <iframe 
                src="http://localhost:8080${narrationData.video_url}" 
                width="100%" 
                height="400" 
                style="border: none; border-radius: 8px;"
                title="MP3by4 Story Video">
              </iframe>
              <p><em>🎭 Interactive HTML video with animated characters and story content</em></p>
            `;
          } else {
            // Handle regular video files
            videoContainer.innerHTML = `
              <h4>🎥 Generated Video:</h4>
              <video controls width="100%">
                <source src="http://localhost:8080${narrationData.video_url}" type="video/mp4">
                Your browser does not support the video element.
              </video>
            `;
          }
          
          resultDiv.appendChild(videoContainer);
        }
        
        // Display generated notes
        if (narrationData.notes) {
          const notesContainer = document.createElement('div');
          notesContainer.className = 'notes-container';
          notesContainer.innerHTML = `
            <h4>📝 Ready-Made Notes:</h4>
            <div class="notes-content">
              ${narrationData.notes.replace(/\n/g, '<br>')}
            </div>
            <button class="copy-notes-btn" onclick="navigator.clipboard.writeText('${narrationData.notes.replace(/'/g, "\\'")}')">
              📋 Copy Notes
            </button>
          `;
          resultDiv.appendChild(notesContainer);
        }
        
        // Display voice options for future use
        if (narrationData.voice_options) {
          const voiceInfoContainer = document.createElement('div');
          voiceInfoContainer.className = 'voice-info';
          voiceInfoContainer.innerHTML = `
            <h4>🎤 Available Voice Types:</h4>
            <ul>
              ${narrationData.voice_options.map(voice => 
                `<li><strong>${voice}:</strong> ${voiceOptions[voice]?.split(' - ')[1] || 'Custom voice'}</li>`
              ).join('')}
            </ul>
          `;
          resultDiv.appendChild(voiceInfoContainer);
        }
        
        addStatus("🎉 Conversion completed successfully!", "success");
        addStatus("💡 You can now download the audio/video and copy the notes", "info");
      }
      
    } catch (error) {
      console.error("Error:", error);
      addStatus(`❌ Error: ${error.message}`, "error");
      
      if (error.message.includes("Failed to fetch")) {
        addStatus("💡 This usually means the server is not running or there's a CORS issue", "info");
        addStatus("🔧 Try reloading the extension and checking the server", "info");
      }
      
      addStatus("💡 Make sure the Python server is running on localhost:8080", "info");
    } finally {
      hideLoading();
    }
  });

  function extractText() {
    // Remove script and style elements
    const scripts = document.querySelectorAll('script, style, nav, header, footer');
    scripts.forEach(el => el.remove());
    
    // Extract text from meaningful elements
    const textElements = [];
    const elements = document.querySelectorAll('h1, h2, h3, h4, h5, h6, p, li, div');
    
    elements.forEach(element => {
      const text = element.textContent.trim();
      if (text && text.length > 20) {
        textElements.push(text);
      }
    });
    
    return textElements.slice(0, 20).join('\n\n');
  }
});

