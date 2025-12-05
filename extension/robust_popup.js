document.addEventListener('DOMContentLoaded', () => {
    const extractBtn = document.getElementById("extractBtn");
    const resultDiv = document.getElementById("result");
    const btnText = document.getElementById("btnText");
    const btnLoading = document.getElementById("btnLoading");

    // 1. Text Extraction Logic
    function getPageContent() {
        // Remove junk
        document.querySelectorAll('script, style, nav, footer, aside').forEach(e => e.remove());
        // Get paragraphs and headers
        let text = "";
        document.querySelectorAll('p, h1, h2, h3').forEach(el => {
            if (el.innerText.length > 30) text += el.innerText + "\n";
        });
        return text.slice(0, 5000); // Limit length
    }

    // 2. Helper to create UI elements
    function addStatus(msg, type) {
        const div = document.createElement("div");
        div.className = `status ${type}`;
        div.innerText = msg;
        resultDiv.appendChild(div);
    }

    // 3. Main Click Handler
    extractBtn.addEventListener("click", async () => {
        // Reset UI
        resultDiv.innerHTML = "";
        btnText.style.display = "none";
        btnLoading.style.display = "inline-block";
        extractBtn.disabled = true;

        try {
            // Get Tab
            let [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

            // Run Script
            const results = await chrome.scripting.executeScript({
                target: { tabId: tab.id },
                func: getPageContent
            });

            if (!results || !results[0] || !results[0].result) {
                throw new Error("No text found on page.");
            }

            const pageText = results[0].result;
            addStatus("🧠 Reading page...", "info");

            // --- THE FIX: Use 127.0.0.1 instead of localhost ---
            console.log("Attempting to connect to server...");
            const response = await fetch('http://127.0.0.1:8080/process', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ content: pageText, url: tab.url })
            });

            console.log("Server response received:", response.status);

            if (!response.ok) {
                // If the server replies with an error, get the text
                const errorText = await response.text();
                throw new Error(`Server Error (${response.status}): ${errorText}`);
            }

            const data = await response.json();

            // Success! Build the UI
            resultDiv.innerHTML = ""; // Clear status
            
            // Create Video Box (only if video URL exists)
            if (data.video_url) {
                const videoBox = document.createElement("div");
                videoBox.className = "media-controls";
                videoBox.innerHTML = `
                    <h4>🎬 Your Video Summary</h4>
                    <video controls autoplay width="100%" style="border-radius:8px; margin-top:5px;">
                        <source src="${data.video_url}?t=${Date.now()}" type="video/mp4">
                    </video>
                `;
                resultDiv.appendChild(videoBox);
            } else {
                addStatus("⚠️ Video generation completed but file not available", "info");
            }

            // Create Script Box
            const scriptBox = document.createElement("div");
            scriptBox.className = "notes-container";
            scriptBox.innerHTML = `
                <h4>📝 AI Script Used:</h4>
                <div class="notes-content">${data.script}</div>
            `;
            resultDiv.appendChild(scriptBox);

            addStatus("✅ Done!", "success");

        } catch (err) {
            console.error("Full Error Details:", err);
            // Show the EXACT error on screen
            addStatus("❌ " + err.message, "error");
            
            if (err.message.includes("Failed to fetch")) {
                 addStatus("💡 Hint: The Extension cannot find the Server. Ensure the black Python window is open.", "info");
            }
        } finally {
            btnText.style.display = "inline";
            btnLoading.style.display = "none";
            extractBtn.disabled = false;
        }
    });
});