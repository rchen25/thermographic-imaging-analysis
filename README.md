# Thermographic Imaging Analysis Agent

A specialized Sports Medicine and Thermographic Imaging system designed to analyze athlete recovery through thermal patterns. This system processes high-resolution temperature grids to identify inflammation, muscle recovery trends, and physiological asymmetries across three workout phases.

## 🚀 Features

- **Automated Thermal Grid Analysis**: Parses complex Excel-based temperature data into numerical arrays.
- **Multi-Phase Tracking**: Compares Pre-workout (Baseline), Post-workout (Acute), and Recovery 48hr (Chronic) phases.
- **Asymmetry Detection**: Quantifies heat distribution differences between left and right limbs to identify potential injury risks.
- **Agentic Recommendations**: Generates clinical recovery protocols (Cryotherapy, Active Recovery, Rest) based on thermal intensity and lingering hotspots.
- **Visual Dashboard**: A modern React-based interface to visualize thermal images and quantitative reports side-by-side.

## 🛠️ Tech Stack

- **Backend**: Python, FastAPI, Pandas, NumPy, OpenPyXL.
- **Frontend**: React, TypeScript, Vite, Lucide Icons.
- **Analysis Engine**: Proprietary logic based on `THERMOGRAPHIC_AGENT.md` mandates.

## 📋 Prerequisites

- Python 3.10+
- Node.js 18+
- npm

## 🔧 Installation & Setup

### 1. Backend Setup
```bash
# Install dependencies
pip install fastapi uvicorn pandas openpyxl numpy

# Start the API server
python3 backend/main.py
```

### 2. Frontend Setup
```bash
cd frontend
# Install dependencies
npm install

# Start the development server
npm run dev
```

## 📈 Analysis Workflow

1. **Baseline Assessment**: Identifies existing "hot spots" and calculates initial asymmetry.
2. **Immediate Response**: Compares Post-workout data against baseline to identify acute inflammation and new asymmetries.
3. **Recovery Evaluation**: Assesses the 48hr delta to verify if thermal signatures have returned to baseline or if lingering heat indicates overtraining.

## 📂 Project Structure

```
├── backend/
│   ├── analyzer.py   # Core thermal analysis logic
│   └── main.py       # FastAPI implementation
├── frontend/
│   ├── src/          # React components & UI
│   └── index.html
├── images/           # Dataset (organized by Session ID)
└── THERMOGRAPHIC_AGENT.md # Agent role & definitions
```

---
*Developed for Sports Medicine Professionals and Athletic Trainers.*
