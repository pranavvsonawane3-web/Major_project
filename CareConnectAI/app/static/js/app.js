// CareConnect AI - Client-side Application Controller

let map = null;
let markersLayer = null;
let currentCoords = { lat: 37.7749, lon: -122.4194 }; // Default SF
let chatHistory = [];
let speechRecognizer = null;

// Initialize on DOM load
document.addEventListener('DOMContentLoaded', () => {
    initTabs();
    initChat();
    initSpeechRecognition();
    initReportDecoder();
    initChecklist();
    initTriage();
    initEmergencyModal();
    initSettingsModal();
    checkBackendStatus();
});

// Backend Health & Status Check
async function checkBackendStatus() {
    try {
        const res = await fetch('/api/status');
        const data = await res.json();
        const geminiBadge = document.getElementById('engine-badge');
        if (data.gemini_connected) {
            geminiBadge.textContent = '✨ Gemini 2.5 Flash Online';
            geminiBadge.classList.add('badge-engine');
        } else {
            geminiBadge.textContent = '⚡ Edge/Offline Intelligence Ready';
        }
    } catch (e) {
        console.warn('Backend status check warning:', e);
    }
}

// Tab Navigation
function initTabs() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabId = btn.getAttribute('data-tab');

            tabBtns.forEach(b => b.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));

            btn.classList.add('active');
            const targetContent = document.getElementById(tabId);
            if (targetContent) {
                targetContent.classList.add('active');
            }

            if (tabId === 'tab-clinics') {
                setTimeout(() => {
                    initMapIfNeeded();
                    loadNearbyClinics();
                }, 150);
            }
        });
    });
}

// Chat System
function initChat() {
    const input = document.getElementById('chat-input');
    const sendBtn = document.getElementById('btn-send');
    const messagesContainer = document.getElementById('chat-messages');
    const chipBtns = document.querySelectorAll('.chip-btn');

    const sendMessage = async (text) => {
        const query = (text || input.value).trim();
        if (!query) return;

        appendMessage('user', query);
        input.value = '';

        // Typing indicator
        const typingId = appendTypingIndicator();

        try {
            const country = document.getElementById('country-select')?.value || 'US';
            const res = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: query,
                    history: chatHistory.slice(-6),
                    country: country
                })
            });
            const data = await res.json();
            removeTypingIndicator(typingId);

            if (data.is_emergency) {
                appendMessage('emergency-alert', data.content);
            } else {
                appendMessage('assistant', data.content);
            }

            // Record to history
            chatHistory.push({ role: 'user', content: query });
            chatHistory.push({ role: 'assistant', content: data.content });

            // If it triggered clinic search, offer to view map
            if (data.type === 'clinic_search') {
                appendQuickAction("🗺️ Open Interactive Map", () => {
                    document.querySelector('[data-tab="tab-clinics"]').click();
                });
            }
        } catch (err) {
            removeTypingIndicator(typingId);
            appendMessage('assistant', "⚠️ Connection error. Please check backend server.");
        }
    };

    sendBtn.addEventListener('click', () => sendMessage());
    input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') sendMessage();
    });

    chipBtns.forEach(chip => {
        chip.addEventListener('click', () => {
            const prompt = chip.getAttribute('data-prompt');
            sendMessage(prompt);
        });
    });
}

function appendMessage(role, text) {
    const container = document.getElementById('chat-messages');
    const bubble = document.createElement('div');
    bubble.className = `message-bubble ${role}`;
    bubble.innerHTML = renderMarkdown(text);
    container.appendChild(bubble);
    container.scrollTop = container.scrollHeight;
}

function appendQuickAction(label, onClick) {
    const container = document.getElementById('chat-messages');
    const actionBtn = document.createElement('button');
    actionBtn.className = 'btn-secondary';
    actionBtn.style.margin = '4px 0 12px 10px';
    actionBtn.textContent = label;
    actionBtn.onclick = onClick;
    container.appendChild(actionBtn);
    container.scrollTop = container.scrollHeight;
}

function appendTypingIndicator() {
    const container = document.getElementById('chat-messages');
    const id = 'typing-' + Date.now();
    const ind = document.createElement('div');
    ind.id = id;
    ind.className = 'message-bubble assistant';
    ind.style.fontStyle = 'italic';
    ind.style.color = '#64748b';
    ind.textContent = 'CareConnect AI is thinking with active medical guardrails...';
    container.appendChild(ind);
    container.scrollTop = container.scrollHeight;
    return id;
}

function removeTypingIndicator(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
}

// Markdown parser
function renderMarkdown(md) {
    if (!md) return '';
    let html = md
        .replace(/^### (.*$)/gim, '<h3 style="margin: 10px 0 6px 0; font-size: 1.05rem;">$1</h3>')
        .replace(/^## (.*$)/gim, '<h2 style="margin: 12px 0 8px 0; font-size: 1.15rem;">$1</h2>')
        .replace(/^# (.*$)/gim, '<h1 style="margin: 14px 0 8px 0; font-size: 1.25rem;">$1</h1>')
        .replace(/\*\*(.*?)\*\*/gim, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/gim, '<em>$1</em>')
        .replace(/`([^`]+)`/gim, '<code style="background:#e2e8f0; padding:2px 5px; border-radius:4px; font-size:0.88em;">$1</code>')
        .replace(/\n\n/gim, '<br><br>')
        .replace(/\n- (.*$)/gim, '<li style="margin-left: 20px;">$1</li>')
        .replace(/\n\d+\. (.*$)/gim, '<li style="margin-left: 20px;">$1</li>');
    return html;
}

// Speech Recognition (Web Speech API)
function initSpeechRecognition() {
    const micBtn = document.getElementById('btn-mic');
    const input = document.getElementById('chat-input');
    if (!micBtn) return;

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
        micBtn.title = 'Speech-to-text not supported in this browser';
        micBtn.style.opacity = '0.5';
        return;
    }

    speechRecognizer = new SpeechRecognition();
    speechRecognizer.continuous = false;
    speechRecognizer.interimResults = false;
    speechRecognizer.lang = 'en-US';

    speechRecognizer.onstart = () => {
        micBtn.classList.add('recording');
        micBtn.textContent = '🛑';
    };

    speechRecognizer.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        input.value = transcript;
    };

    speechRecognizer.onend = () => {
        micBtn.classList.remove('recording');
        micBtn.textContent = '🎤';
    };

    micBtn.addEventListener('click', () => {
        if (micBtn.classList.contains('recording')) {
            speechRecognizer.stop();
        } else {
            speechRecognizer.start();
        }
    });
}

// Medical Report Decoder
function initReportDecoder() {
    const textarea = document.getElementById('report-textarea');
    const decodeBtn = document.getElementById('btn-decode-report');
    const resultsContainer = document.getElementById('report-results');
    const dropzone = document.getElementById('file-dropzone');
    const fileInput = document.getElementById('report-file-input');

    // Sample buttons
    const sampleCbc = document.getElementById('sample-cbc');
    const sampleLipid = document.getElementById('sample-lipid');
    const sampleCmp = document.getElementById('sample-cmp');

    if (sampleCbc) {
        sampleCbc.addEventListener('click', () => {
            textarea.value = `COMPLETE BLOOD COUNT (CBC):
WBC (White Blood Cells): 12.4 x10^3/uL (Standard: 4.5 - 11.0) HIGH
Hemoglobin: 11.2 g/dL (Standard: 12.0 - 17.5) LOW
Hematocrit: 34.8 % (Standard: 36.0 - 50.0) LOW
Platelet Count: 310 x10^3/uL (Standard: 150 - 450) NORMAL`;
        });
    }

    if (sampleLipid) {
        sampleLipid.addEventListener('click', () => {
            textarea.value = `LIPID / CHOLESTEROL PANEL:
Total Cholesterol: 235 mg/dL (Desirable: < 200) HIGH
LDL Cholesterol: 154 mg/dL (Optimal: < 100) HIGH
HDL Cholesterol: 42 mg/dL (Desirable: > 40) NORMAL
Triglycerides: 195 mg/dL (Normal: < 150) HIGH`;
        });
    }

    if (sampleCmp) {
        sampleCmp.addEventListener('click', () => {
            textarea.value = `METABOLIC & GLYCEMIC PANEL:
Fasting Blood Glucose: 114 mg/dL (Standard: 70 - 99) HIGH
HbA1c: 6.2 % (Normal: < 5.7) ELEVATED
Serum Creatinine: 1.1 mg/dL (Standard: 0.6 - 1.3) NORMAL
ALT (Liver Enzyme): 58 U/L (Standard: 7 - 56) HIGH
TSH: 2.4 uIU/mL (Standard: 0.4 - 4.5) NORMAL
Vitamin D: 19 ng/mL (Optimal: 30 - 100) LOW`;
        });
    }

    decodeBtn.addEventListener('click', async () => {
        const text = textarea.value.trim();
        if (!text) {
            alert('Please paste lab report text or choose a sample report.');
            return;
        }

        resultsContainer.innerHTML = '<div style="padding: 20px; color:#64748b;">Decoding report with medical knowledge base...</div>';

        try {
            const res = await fetch('/api/report/decode', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text })
            });
            const data = await res.json();
            renderReportResults(data);
        } catch (e) {
            resultsContainer.innerHTML = '<div style="color:red;">Error processing lab report.</div>';
        }
    });

    // File Dropzone
    if (dropzone && fileInput) {
        dropzone.addEventListener('click', () => fileInput.click());
        fileInput.addEventListener('change', async (e) => {
            const file = e.target.files[0];
            if (!file) return;

            const formData = new FormData();
            formData.append('file', file);

            resultsContainer.innerHTML = '<div style="padding: 20px; color:#64748b;">Analyzing uploaded document...</div>';

            try {
                const res = await fetch('/api/report/upload', {
                    method: 'POST',
                    body: formData
                });
                const data = await res.json();
                renderReportResults(data);
            } catch (err) {
                resultsContainer.innerHTML = '<div style="color:red;">Failed to process uploaded file.</div>';
            }
        });
    }
}

function renderReportResults(data) {
    const container = document.getElementById('report-results');
    if (!container) return;

    let html = `
        <div style="margin-bottom: 20px;">
            <div style="font-size: 1.15rem; font-weight: 700; color: #0f172a; margin-bottom: 8px;">
                📋 Lab Report Analysis Summary
            </div>
            <div style="background: #f1f5f9; padding: 14px; border-radius: 8px; font-size: 0.9rem; line-height: 1.6;">
                ${renderMarkdown(data.summary)}
            </div>
        </div>
    `;

    if (data.biomarkers && data.biomarkers.length > 0) {
        html += `<h4 style="margin: 16px 0 10px 0; font-size: 0.95rem; font-weight: 700;">🔍 Detailed Biomarker Breakdown:</h4>`;
        data.biomarkers.forEach(b => {
            html += `
                <div class="biomarker-card ${b.status_color}">
                    <div class="biomarker-header">
                        <strong>${b.name}</strong>
                        <span class="status-pill ${b.status_color}">${b.status}</span>
                    </div>
                    <div style="font-size: 0.88rem; color: #334155; margin-bottom: 6px;">
                        <strong>Value:</strong> ${b.value} ${b.unit} &nbsp;|&nbsp; <strong>Reference:</strong> ${b.standard_range} ${b.unit}
                    </div>
                    <div style="font-size: 0.85rem; color: #475569; margin-bottom: 4px;">
                        💡 <strong>In Plain Words:</strong> ${b.analogy}
                    </div>
                    ${b.lifestyle_factors ? `
                        <div style="font-size: 0.82rem; color: #64748b; margin-bottom: 4px;">
                            🌱 <strong>Non-Disease Factors:</strong> ${b.lifestyle_factors}
                        </div>
                    ` : ''}
                </div>
            `;
        });
    }

    if (data.questions_for_doctor && data.questions_for_doctor.length > 0) {
        html += `
            <div style="margin-top: 20px; background: #e0f2fe; border: 1px solid #bae6fd; padding: 16px; border-radius: 10px;">
                <div style="font-weight: 700; color: #0369a1; margin-bottom: 8px;">
                    🗣️ Smart Questions to Ask Your Doctor:
                </div>
                <ul style="margin-left: 20px; font-size: 0.88rem; color: #075985;">
                    ${data.questions_for_doctor.map(q => `<li style="margin-bottom: 4px;">${q}</li>`).join('')}
                </ul>
            </div>
        `;
    }

    container.innerHTML = html;
}

// Leaflet Map & Clinic Locator
function initMapIfNeeded() {
    if (map) return;
    const mapEl = document.getElementById('map');
    if (!mapEl) return;

    map = L.map('map').setView([currentCoords.lat, currentCoords.lon], 13);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);

    markersLayer = L.layerGroup().addTo(map);

    // Geolocation button
    const locateBtn = document.getElementById('btn-get-location');
    if (locateBtn) {
        locateBtn.addEventListener('click', () => {
            if (navigator.geolocation) {
                locateBtn.textContent = '⏳ Locating...';
                navigator.geolocation.getCurrentPosition(
                    (pos) => {
                        currentCoords.lat = pos.coords.latitude;
                        currentCoords.lon = pos.coords.longitude;
                        locateBtn.textContent = '📍 My Location Acquired';
                        map.setView([currentCoords.lat, currentCoords.lon], 13);
                        loadNearbyClinics();
                    },
                    (err) => {
                        alert('Could not retrieve GPS coordinates. Defaulting to demo coordinates.');
                        locateBtn.textContent = '📍 Use My Location';
                    }
                );
            }
        });
    }

    // Filter selector
    const filterSelect = document.getElementById('clinic-filter');
    if (filterSelect) {
        filterSelect.addEventListener('change', () => loadNearbyClinics());
    }
}

async function loadNearbyClinics() {
    const listContainer = document.getElementById('clinic-cards');
    const filterSelect = document.getElementById('clinic-filter');
    const facilityType = filterSelect ? filterSelect.value : 'all';

    if (listContainer) {
        listContainer.innerHTML = '<div style="padding: 16px; color:#64748b;">Finding nearby healthcare centers...</div>';
    }

    try {
        const url = `/api/clinics?lat=${currentCoords.lat}&lon=${currentCoords.lon}&facility_type=${facilityType}`;
        const res = await fetch(url);
        const data = await res.json();

        markersLayer.clearLayers();
        listContainer.innerHTML = '';

        if (!data.facilities || data.facilities.length === 0) {
            listContainer.innerHTML = '<div style="padding: 16px;">No healthcare centers found within radius.</div>';
            return;
        }

        // Add user marker
        const userMarker = L.circleMarker([currentCoords.lat, currentCoords.lon], {
            radius: 8,
            fillColor: '#0284c7',
            color: '#ffffff',
            weight: 3,
            fillOpacity: 1
        }).addTo(markersLayer).bindPopup('<strong>📍 You Are Here</strong>');

        data.facilities.forEach((fac, idx) => {
            const card = document.createElement('div');
            card.className = 'clinic-card';
            const badgeBg = fac.is_emergency ? 'background:#fee2e2; color:#b91c1c;' : 'background:#e0f2fe; color:#0369a1;';

            card.innerHTML = `
                <div style="display:flex; justify-content:space-between; align-items:start; margin-bottom:4px;">
                    <strong style="font-size:0.92rem; color:#0f172a;">${fac.name}</strong>
                    <span style="font-size:0.72rem; font-weight:700; padding:2px 8px; border-radius:9999px; ${badgeBg}">
                        ${fac.distance_miles ? fac.distance_miles + ' mi' : fac.distance_km + ' km'}
                    </span>
                </div>
                <div style="font-size:0.8rem; color:#475569; margin-bottom:4px;">📍 ${fac.address}</div>
                <div style="font-size:0.78rem; color:#64748b; margin-bottom:6px;">🕒 ${fac.hours}</div>
                <div style="display:flex; gap:8px;">
                    <a href="tel:${fac.phone}" class="chip-btn" style="text-decoration:none;">📞 Call</a>
                    <a href="https://www.google.com/maps/dir/?api=1&destination=${fac.lat},${fac.lon}" target="_blank" class="chip-btn" style="text-decoration:none;">🧭 Directions</a>
                </div>
            `;

            // Marker
            const markerColor = fac.is_emergency ? '#dc2626' : (fac.type === 'pharmacy' ? '#16a34a' : '#0284c7');
            const marker = L.circleMarker([fac.lat, fac.lon], {
                radius: 7,
                fillColor: markerColor,
                color: '#fff',
                weight: 2,
                fillOpacity: 0.9
            }).addTo(markersLayer);

            marker.bindPopup(`
                <strong>${fac.name}</strong><br>
                <span>${fac.type_label}</span><br>
                <span>📞 ${fac.phone}</span><br>
                <span>🕒 ${fac.hours}</span><br>
                <a href="https://www.google.com/maps/dir/?api=1&destination=${fac.lat},${fac.lon}" target="_blank">Get Directions</a>
            `);

            card.addEventListener('click', () => {
                document.querySelectorAll('.clinic-card').forEach(c => c.classList.remove('selected'));
                card.classList.add('selected');
                map.setView([fac.lat, fac.lon], 15);
                marker.openPopup();
            });

            listContainer.appendChild(card);
        });
    } catch (e) {
        if (listContainer) listContainer.innerHTML = '<div style="color:red; padding:16px;">Failed to load clinics.</div>';
    }
}

// Appointment Preparation Checklist
function initChecklist() {
    const btnGenerate = document.getElementById('btn-generate-checklist');
    const briefContainer = document.getElementById('checklist-output');
    const btnCopy = document.getElementById('btn-copy-brief');
    const btnPrint = document.getElementById('btn-print-brief');

    btnGenerate.addEventListener('click', async () => {
        const complaint = document.getElementById('prep-complaint').value.trim();
        const duration = document.getElementById('prep-duration').value.trim();
        const severity = parseInt(document.getElementById('prep-severity').value || '5');
        const medsRaw = document.getElementById('prep-meds').value.trim();
        const allergiesRaw = document.getElementById('prep-allergies').value.trim();
        const customConcerns = document.getElementById('prep-concerns').value.trim();

        if (!complaint) {
            alert('Please provide the main reason or symptoms for your appointment.');
            return;
        }

        const medications = medsRaw ? medsRaw.split('\n').map(s => s.trim()).filter(Boolean) : [];
        const allergies = allergiesRaw ? allergiesRaw.split('\n').map(s => s.trim()).filter(Boolean) : [];

        briefContainer.textContent = 'Generating comprehensive consultation brief...';

        try {
            const res = await fetch('/api/checklist/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    chief_complaint: complaint,
                    duration,
                    severity,
                    medications,
                    allergies,
                    custom_concerns: customConcerns
                })
            });
            const data = await res.json();
            briefContainer.textContent = data.formatted_markdown;
        } catch (e) {
            briefContainer.textContent = 'Error generating checklist.';
        }
    });

    if (btnCopy) {
        btnCopy.addEventListener('click', () => {
            const text = briefContainer.textContent;
            navigator.clipboard.writeText(text).then(() => alert('Consultation brief copied to clipboard!'));
        });
    }

    if (btnPrint) {
        btnPrint.addEventListener('click', () => {
            const printWin = window.open('', '_blank');
            printWin.document.write(`<html><head><title>Consultation Brief</title></head><body style="font-family:sans-serif; padding:40px; line-height:1.6;"><pre style="white-space:pre-wrap; font-family:inherit;">${briefContainer.textContent}</pre></body></html>`);
            printWin.document.close();
            printWin.print();
        });
    }
}

// Care Triage ("Where Should I Go?")
function initTriage() {
    const triageBtn = document.getElementById('btn-triage');
    const input = document.getElementById('triage-input');
    const resultBox = document.getElementById('triage-result');
    const chipBtns = document.querySelectorAll('.triage-chip');

    const runTriage = async (symptom) => {
        if (!symptom) return;
        resultBox.innerHTML = '<div style="color:#64748b;">Evaluating appropriate care tier...</div>';

        try {
            const res = await fetch('/api/triage', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ symptom })
            });
            const data = await res.json();

            resultBox.innerHTML = `
                <div style="background:white; border:1px solid #e2e8f0; border-radius:12px; padding:20px; box-shadow:0 2px 4px rgba(0,0,0,0.05);">
                    <div style="font-size:1.15rem; font-weight:700; color:#0f172a; margin-bottom:8px;">
                        ${data.recommendation}
                    </div>
                    <div style="font-size:0.9rem; color:#334155; margin-bottom:12px; line-height:1.6;">
                        <strong>Why:</strong> ${data.reasoning}
                    </div>
                    <div style="background:#f8fafc; border-left:4px solid #0284c7; padding:10px 14px; font-size:0.85rem; color:#475569;">
                        <strong>Standard Criteria:</strong> ${data.level_info?.when_to_go || ''}
                    </div>
                </div>
            `;
        } catch (e) {
            resultBox.innerHTML = '<div style="color:red;">Error evaluating triage request.</div>';
        }
    };

    if (triageBtn && input) {
        triageBtn.addEventListener('click', () => runTriage(input.value.trim()));
    }

    chipBtns.forEach(c => {
        c.addEventListener('click', () => {
            const s = c.getAttribute('data-symptom');
            input.value = s;
            runTriage(s);
        });
    });
}

// Emergency Modal
function initEmergencyModal() {
    const modal = document.getElementById('emergency-modal');
    const openBtn = document.getElementById('btn-emergency-top');
    const closeBtn = document.getElementById('btn-close-emergency');
    const countrySelect = document.getElementById('emergency-country-select');

    if (openBtn && modal) {
        openBtn.addEventListener('click', () => modal.showModal());
    }
    if (closeBtn && modal) {
        closeBtn.addEventListener('click', () => modal.close());
    }

    if (countrySelect) {
        countrySelect.addEventListener('change', updateEmergencyNumbers);
        updateEmergencyNumbers();
    }
}

async function updateEmergencyNumbers() {
    const code = document.getElementById('emergency-country-select')?.value || 'US';
    try {
        const res = await fetch('/api/emergency/hotlines');
        const data = await res.json();
        const country = data.countries[code] || data.countries['US'];

        document.getElementById('em-number-general').textContent = country.general;
        document.getElementById('em-number-general-link').href = `tel:${country.general}`;

        document.getElementById('em-number-crisis').textContent = country.mental_health_crisis;
        document.getElementById('em-number-crisis-link').href = `tel:${country.mental_health_crisis}`;

        document.getElementById('em-number-poison').textContent = country.poison_control;
    } catch (e) {
        console.warn('Could not update emergency hotlines', e);
    }
}

// Settings Modal
function initSettingsModal() {
    const modal = document.getElementById('settings-modal');
    const openBtn = document.getElementById('btn-settings-open');
    const closeBtn = document.getElementById('btn-close-settings');
    const saveBtn = document.getElementById('btn-save-key');
    const keyInput = document.getElementById('settings-gemini-key');

    if (openBtn && modal) {
        openBtn.addEventListener('click', () => modal.showModal());
    }
    if (closeBtn && modal) {
        closeBtn.addEventListener('click', () => modal.close());
    }

    if (saveBtn && keyInput) {
        saveBtn.addEventListener('click', async () => {
            const key = keyInput.value.trim();
            if (!key) return;

            saveBtn.textContent = 'Verifying...';
            try {
                const res = await fetch('/api/config/api-key', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ api_key: key })
                });
                const data = await res.json();
                alert(data.message);
                modal.close();
                checkBackendStatus();
            } catch (e) {
                alert('Failed to configure API key.');
            } finally {
                saveBtn.textContent = 'Save API Key';
            }
        });
    }
}
