from fastapi import FastAPI

app = FastAPI(
    title="RapidMaternal API",
    description="Real-time maternal emergency response system",
    version="0.1.0"
)

@app.get("/")
def health_check():
    return {"status": "RapidMaternal backend running"}