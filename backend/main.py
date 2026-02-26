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

# Serve static images
app.mount("/images", StaticFiles(directory="images"), name="images")

analyzer = ThermographicAnalyzer("images")

@app.get("/sessions")
async def list_sessions():
    sessions = [d for d in os.listdir("images") if os.path.isdir(os.path.join("images", d))]
    return {"sessions": sessions}

@app.get("/analyze/{session_id}")
async def analyze_session(session_id: str):
    try:
        report = analyzer.analyze_session(session_id)
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
