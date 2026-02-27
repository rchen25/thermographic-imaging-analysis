# Gemini Context & Mandates

This file provides the foundational context for any Gemini CLI session working on the Thermographic Imaging Analysis project.

## Project Mission
To provide high-precision thermal analysis for sports medicine, focusing on limb segmentation and physiological asymmetry detection across baseline, acute, and recovery phases.

## Architectural Mandates
- **Single Port Rule**: Both the FastAPI backend and React frontend must be served from a single port (default 8000). The backend handles static file serving for the compiled frontend.
- **Vision Pipeline**: Use OpenCV for thermal segmentation. Always isolate skin from background using thermal thresholding (~26°C-38°C) before calculating metrics.
- **Anatomical ROI**: Always segment the legs into Upper (Quad/Hamstring) and Lower (Shin/Calf) regions for granular reporting.
- **Reasoning Pipeline**: Use LangGraph for the diagnostic workflow to maintain a stateful, traceable analysis graph.

## Technical Constraints
- **Backend**: FastAPI, OpenCV-Headless, LangGraph, Pandas, NumPy.
- **Frontend**: Vite + React (TypeScript).
- **Dependency Management**: Use `uv` for Python environment and package execution.
- **Relative Paths**: Avoid hardcoding `localhost:8000` in the frontend; use relative API paths to support unified port serving.

## Domain Knowledge
- **Thermal Markers**: Hotter areas (Red/White) indicate inflammation or metabolic activity.
- **Asymmetry**: A deviation > 1.2°C is generally considered a "High Risk" pathological marker.
- **Ambient Correction**: Always calculate skin temperature relative to the background environment mean to account for fluctuating room temperatures.
