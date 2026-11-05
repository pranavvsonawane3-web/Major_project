# 🩺 CareConnect AI — Healthcare Assistance Agent

> **An empathetic, highly reliable, and compliant AI healthcare assistant designed to bridge health literacy, demystify medical reports, and navigate healthcare services without crossing diagnostic or prescriptive boundaries.**

---

## 🌟 Key Features

### 1. 📄 Medical Report Simplifier
- **Plain-English Translation:** Translates complex laboratory jargon into accessible analogies (e.g., *WBCs* $\rightarrow$ "the body's security guards"; *HbA1c* $\rightarrow$ "a 90-day video of blood sugar rather than a snapshot").
- **Biomarker Range Contextualizer:** Understands reference intervals across Complete Blood Counts (CBC), Lipid/Cholesterol Panels, Metabolic Panels (CMP), Liver Enzymes, Glycemic markers, and Thyroid tests.
- **Lifestyle Context:** Explains common non-disease factors (hydration level, stress, recent meals, exercise) that can influence test values.
- **Doctor Conversation Starters:** Suggests smart, targeted questions to ask your doctor.

### 2. 📍 Nearby Care Locator & Interactive Map
- **Hospitals, Urgent Care, Clinics & Pharmacies:** Locates nearby healthcare facilities using real OpenStreetMap Overpass queries and high-reliability local geo-caches.
- **Interactive Leaflet Map:** Displays color-coded facility markers (Red: Emergency/ER, Blue: Clinic, Orange: Urgent Care, Green: Pharmacy).
- **One-Click Actions:** Click-to-call phone numbers, current operating hours, and direct Google Maps / GPS directions.

### 3. 📋 Doctor Appointment Preparation Checklist
- **Consultation Brief Generator:** Synthesizes the chief complaint, duration, pain scale (1–10), daily medications, and allergies.
- **Personalized Questions:** Automatically tailors the top 5 questions to ask your physician during the consultation.
- **What to Bring:** Checklist for insurance cards, ID, past lab reports, and medication bottles.
- **Export & Print:** One-click copy to clipboard or print for consultation day.

### 4. 🧭 "Where Should I Go?" — Healthcare Triage Guide
- **Level of Care Guidance:** Categorizes user symptoms into the appropriate care tier:
  - 🚨 **Emergency Room (ER):** Life- or limb-threatening symptoms.
  - ⚡ **Urgent Care:** Same-day walk-in care (sprains, cuts needing stitches, minor burns).
  - 🩺 **Primary Care / Telehealth:** Routine checkups, chronic disease management.
  - 🔬 **Specialist Referral:** Cardiology, Dermatology, Orthopedics, Neurology, Gastroenterology, ENT, etc.

### 5. 🚨 Emergency Protocols & Global Hotline Directory
- **Red-Flag Interceptor:** Detects critical symptoms (chest pain, stroke signs [FAST], acute breathing distress, severe bleeding, crisis/self-harm) and immediately surfaces emergency directives.
- **Country Hotlines:** Emergency and crisis hotlines for the United States (`911` / `988`), United Kingdom (`999` / `111`), Canada (`911` / `988`), Australia (`000` / `13 11 14`), India (`112` / `14416`), and the European Union (`112`).
- **Emergency Dispatcher Script:** 4-step checklist on what to communicate to the emergency operator.

---

## 🛡️ Medical Safety & Ethics Guardrails

**Core Directive:** CareConnect AI strictly **does NOT diagnose diseases or prescribe medications.**

1. **Input Guardrail:** Intercepts requests like *"Diagnose me"*, *"Do I have diabetes?"*, or *"What antibiotic should I take?"* and redirects the user with educational explanations and care navigation.
2. **Output Sanitizer:** Scans all generated responses to strip out any declarative diagnostic phrasing or medication dosage suggestions.
3. **Mandatory Disclaimer:** Every analysis and chat turn carries a clear medical disclaimer reminding users to consult licensed medical professionals.

---

## 🏗️ Architecture

```
CareConnectAI/
├── app/
│   ├── main.py                     # FastAPI REST API & static file server
│   ├── agent/
│   │   ├── orchestrator.py         # Master agent coordinator & router
│   │   ├── guardrails.py           # Medical safety validator (non-diagnostic/prescriptive)
│   │   ├── emergency_agent.py      # Red-flag detector & emergency hotline provider
│   │   ├── report_decoder.py       # Plain-English lab report simplifier
│   │   ├── clinic_finder.py        # Location-based clinic & hospital finder
│   │   ├── checklist_agent.py      # Doctor appointment prep brief generator
│   │   ├── service_locator.py      # Triage and specialty routing
│   │   └── gemini_client.py        # Optional Google Gemini multimodal API client
│   ├── data/
│   │   ├── emergency_numbers.json  # Global hotlines and red-flag catalog
│   │   ├── lab_tests_knowledge.json# Biomarkers, analogies, and reference ranges
│   │   └── specialties_map.json    # Healthcare tiers & symptom mapping
│   └── static/
│       ├── index.html              # Responsive web interface
│       ├── css/style.css           # Clean modern medical styling
│       └── js/app.js               # Client controller (Map, Chat, Voice, Checklist)
├── sample_reports/                 # Sample test reports for 1-click testing
├── tests/                          # Pytest verification suite (18 unit tests)
├── requirements.txt
├── server.py                       # Python server launcher
├── start.bat                       # Windows 1-click launcher
└── README.md
```

---

## 🚀 Getting Started

### 1. Requirements
- Python 3.10+
- Installed packages: `fastapi`, `uvicorn`, `python-multipart`, `requests`, `pydantic`, `pytest`

### 2. Run the Application
In your terminal, navigate to `d:\Project\CareConnectAI`:
```bash
python server.py
```
Or simply double-click `start.bat`.

Then open your browser at:
👉 **`http://127.0.0.1:8000`**

### 3. Run Automated Tests
```bash
python -m pytest tests -v
```
All 18 unit tests cover guardrails, emergency detection, report decoding, and API endpoints.

---

## 🔌 Optional: Google Gemini API Integration
CareConnect AI functions **100% offline out-of-the-box** using its built-in medical rule engine and knowledge bases.
To enable multimodal photo uploads of lab reports or expanded conversational nuance:
1. Open the web app.
2. Click **⚙️ Settings** in the top navigation bar.
3. Enter your **Google Gemini API Key** and click Save.
