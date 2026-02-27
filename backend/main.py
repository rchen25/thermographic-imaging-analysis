from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from analyzer import ThermographicAnalyzer
import os

app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize analyzer
images_path = os.path.join(os.path.dirname(__file__), "..", "images")
analyzer = ThermographicAnalyzer(images_path)

# API Routes must come before mounting the frontend at "/"
@app.get("/sessions")
async def list_sessions():
    # Use the absolute images_path determined above
    sessions = [d for d in os.listdir(images_path) if os.path.isdir(os.path.join(images_path, d))]
    return {"sessions": sessions}

@app.get("/analyze/{session_id}")
async def analyze_session(session_id: str):
    try:
        report = analyzer.analyze_session(session_id)
        return report
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# Serve static images
app.mount("/images", StaticFiles(directory=images_path), name="images")

# Serve frontend
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
