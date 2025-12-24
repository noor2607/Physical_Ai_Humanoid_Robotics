from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.chat import router

app = FastAPI(title="AI Humanoid Book RAG")

# Add CORS middleware to allow requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the exact frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "AI Humanoid Book RAG API is running"}
