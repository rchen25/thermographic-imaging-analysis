# Thermographic Imaging Analysis Agent

A specialized Sports Medicine and Thermographic Imaging system designed to analyze athlete recovery through thermal patterns. This system integrates Computer Vision for precise limb segmentation and LangGraph for intelligent diagnostic reasoning.

## 🚀 Features

- **CV-Powered ROI Extraction**: Automatically segments human skin from background noise using thermal thresholding and contour detection.
- **LangGraph Reasoning Pipeline**: Uses a state-based graph to chain clinical interpretation, risk assessment, and recovery planning.
- **Unified Single-Port Architecture**: Serves both the React frontend and FastAPI backend from a single port (8000) for simplified deployment.
- **Multi-Phase Tracking**: Compares Pre-workout (Baseline), Post-workout (Acute), and Recovery 48hr (Chronic) phases.
- **Visual Dashboard**: Modern React interface to visualize segmented thermal data and agentic reports.

## 🛠️ Tech Stack

- **Backend**: Python, FastAPI, LangGraph, OpenCV, Pandas, NumPy.
- **Frontend**: React, TypeScript, Vite.
- **Dependency Management**: `uv` (Fastest Python package installer/runner).

## 🔧 Launch Instructions

The entire system is unified into a single launch script.

### Prerequisites
- [uv](https://github.com/astral-sh/uv) installed (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- Node.js 18+ & npm

### Start the Application
```bash
chmod +x launch.sh
./launch.sh
```

**Access the Dashboard:** [http://localhost:8000](http://localhost:8000)

## 📂 Project Structure

```
├── backend/
│   ├── main.py        # FastAPI Entry point & Static File Serving
│   ├── analyzer.py    # Orchestration of Vision & Graph pipelines
│   ├── processor.py   # Computer Vision (OpenCV) Segmentation
│   └── graph.py       # LangGraph Diagnostic Workflow
├── frontend/
│   ├── src/           # React components
│   └── dist/          # Compiled production build (served by backend)
├── images/            # Dataset (Raw PNGs + Excel Temperature Grids)
└── launch.sh          # Unified build & run script
```

---
*Developed for Sports Medicine Professionals and Athletic Trainers.*
