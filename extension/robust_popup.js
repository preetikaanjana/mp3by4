// Change this to your deployed backend URL (e.g. "https://preetika-mp3by4.onrender.com")
const SERVER_URL = "https://mp3by4-backend.onrender.com"; // If using Render

document.addEventListener('DOMContentLoaded', () => {
    const extractBtn = document.getElementById("extractBtn");
    const btnText = document.getElementById("btnText");
    const btnLoading = document.getElementById("btnLoading");
    const statusBox = document.getElementById("statusBox");
    const resultBox = document.getElementById("resultBox");
    
    const videoContainer = document.getElementById("videoContainer");
    const notesContent = document.getElementById("notesContent");
    const scriptContent = document.getElementById("scriptContent");
    const summaryLengthSelect = document.getElementById("summaryLength");

    // Hold the parsed notes text globally for copy functionality
    let currentNotes = [];

    // --- TAB SWITCHING LOGIC ---
    window.switchTab = (tabName) => {
        // Toggle tab button active state
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        const activeBtn = document.getElementById(`btnTab${tabName.charAt(0).toUpperCase() + tabName.slice(1)}`);
        if (activeBtn) activeBtn.classList.add('active');

        // Toggle pane visibility
        document.querySelectorAll('.tab-pane').forEach(pane => {
            pane.classList.remove('active');
        });
        const activePane = document.getElementById(`pane${tabName.charAt(0).toUpperCase() + tabName.slice(1)}`);
        if (activePane) activePane.classList.add('active');
    };

    // --- CHARACTER PILL SELECTION LOGIC ---
    window.selectPill = (charName) => {
        // Remove selected class from all pills
        document.querySelectorAll('.character-pill').forEach(pill => {
            pill.classList.remove('selected');
        });

        // Add selected class to the clicked pill
        if (charName === 'girl') {
            document.getElementById('pillRachel').classList.add('selected');
            document.getElementById('charRachel').checked = true;
        } else if (charName === 'robot') {
            document.getElementById('pillSheldon').classList.add('selected');
            document.getElementById('charSheldon').checked = true;
        } else if (charName === 'news_anchor') {
            document.getElementById('pillMichael').classList.add('selected');
            document.getElementById('charMichael').checked = true;
        }
    };

    // Bind click event listeners dynamically to satisfy Chrome Extension CSP
    document.getElementById('pillRachel').addEventListener('click', () => window.selectPill('girl'));
    document.getElementById('pillSheldon').addEventListener('click', () => window.selectPill('robot'));
    document.getElementById('pillMichael').addEventListener('click', () => window.selectPill('news_anchor'));

    document.getElementById('btnTabVideo').addEventListener('click', () => window.switchTab('video'));
    document.getElementById('btnTabNotes').addEventListener('click', () => window.switchTab('notes'));
    document.getElementById('btnTabScript').addEventListener('click', () => window.switchTab('script'));

    // --- STATUS INJECTOR ---
    function addStatus(msg, type) {
        statusBox.innerHTML = ""; // Clear existing status
        const div = document.createElement("div");
        div.className = `status-msg ${type}`;
        div.innerText = msg;
        statusBox.appendChild(div);
    }

    // --- WEB SCRAPER ---
    function getPageContent() {
        // Remove junk elements to clean input text
        const clone = document.documentElement.cloneNode(true);
        clone.querySelectorAll('script, style, nav, footer, aside, iframe, noscript').forEach(e => e.remove());
        
        let text = "";
        clone.querySelectorAll('p, h1, h2, h3, article').forEach(el => {
            const t = el.innerText.trim();
            if (t.length > 25) text += t + "\n";
        });
        return text.slice(0, 6000); // Send up to 6000 characters
    }

    // --- CONVERT BUTTON EVENT ---
    extractBtn.addEventListener("click", async () => {
        // Reset UI States
        statusBox.innerHTML = "";
        resultBox.style.display = "none";
        videoContainer.innerHTML = "";
        notesContent.innerHTML = "";
        scriptContent.innerText = "";
        
        btnText.style.display = "none";
        btnLoading.style.display = "inline-block";
        extractBtn.disabled = true;

        try {
            // 1. Fetch current tab
            const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
            if (!tab) {
                throw new Error("No active tab found. Open a webpage first!");
            }

            addStatus("🕵️‍♂️ Scraping webpage content...", "info");

            // 2. Execute scraping script in active tab
            let pageText = "";
            try {
                const results = await chrome.scripting.executeScript({
                    target: { tabId: tab.id },
                    func: getPageContent
                });
                pageText = results[0]?.result || "";
            } catch (scrErr) {
                console.warn("Could not scrape page dynamically:", scrErr);
            }

            // Fallback: If scraper fails, the backend server will attempt to scrape the URL directly
            if (!pageText && !tab.url) {
                throw new Error("Could not extract page content and no valid URL was found.");
            }

            // 3. Gather user parameters
            const selectedCharacter = document.querySelector('input[name="character"]:checked')?.value || 'girl';
            const selectedLength = summaryLengthSelect.value || 'medium';

            const charLabel = selectedCharacter === 'robot' ? 'Sheldon Cooper' : 
                              selectedCharacter === 'news_anchor' ? 'Michael Scott' : 'Rachel Green';

            addStatus(`🎭 Sending to ${charLabel}...`, "info");

            // 4. Fire POST request to Flask Backend
            const response = await fetch(`${SERVER_URL}/process`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    content: pageText,
                    url: tab.url,
                    character_name: selectedCharacter,
                    summary_length: selectedLength
                })
            });

            if (!response.ok) {
                const errText = await response.text();
                throw new Error(`Server Error: ${errText || response.statusText}`);
            }

            const data = await response.json();
            
            // 5. Build and Populate UI
            addStatus("✅ Generation completed!", "success");

            // Populating Video Tab
            if (data.video_url) {
                videoContainer.innerHTML = `
                    <video id="resultVideo" controls autoplay>
                        <source src="${data.video_url}?t=${Date.now()}" type="video/mp4">
                    </video>
                `;
            } else {
                videoContainer.innerHTML = `<p style="font-size:11px;color:var(--text-gray);">Video summary file is unavailable.</p>`;
            }

            // Populating Notes Tab
            if (data.notes && data.notes.length > 0) {
                currentNotes = data.notes;
                let notesHtml = "<ul>";
                data.notes.forEach(note => {
                    notesHtml += `<li>${note}</li>`;
                });
                notesHtml += "</ul>";
                notesContent.innerHTML = notesHtml;
            } else {
                notesContent.innerHTML = "<p>No bullet notes generated.</p>";
            }

            // Populating Script Tab
            scriptContent.innerText = data.script || "No script generated.";

            // Show container & default to Video Tab
            resultBox.style.display = "block";
            window.switchTab('video');

        } catch (err) {
            console.error("Popup Error:", err);
            addStatus(`❌ ${err.message}`, "error");
            if (err.message.includes("Failed to fetch")) {
                const hint = document.createElement("div");
                hint.className = "status-msg info";
                hint.style.marginTop = "5px";
                hint.innerText = "💡 Tip: Make sure the black Python server window is running on your computer.";
                statusBox.appendChild(hint);
            }
        } finally {
            btnText.style.display = "inline";
            btnLoading.style.display = "none";
            extractBtn.disabled = false;
        }
    });

    // --- COPY NOTES ---
    document.getElementById("copyNotesBtn").addEventListener("click", () => {
        if (currentNotes.length === 0) return;
        const textToCopy = currentNotes.map(n => '• ' + n).join('\n');
        navigator.clipboard.writeText("MP3by4 Sitcom Notes:\n" + textToCopy).then(() => {
            const copyBtn = document.getElementById("copyNotesBtn");
            const originalText = copyBtn.innerText;
            copyBtn.innerText = "Notes Copied! ✓";
            copyBtn.style.background = "#4e9f90";
            setTimeout(() => {
                copyBtn.innerText = originalText;
                copyBtn.style.background = "var(--pastel-green)";
            }, 1500);
        });
    });
});