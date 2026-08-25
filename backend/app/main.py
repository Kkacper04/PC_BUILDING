from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.api.v1.components import router as components_router
from app.api.v1.builds import router as builds_router

app = FastAPI(
    title="PC Builder API",
    description="API for checking PC component compatibility and AI-powered recommendations.",
    version="1.0.0",
)

# CORS — allow frontend (Next.js dev server) to talk to the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(components_router, prefix="/api/v1")
app.include_router(builds_router, prefix="/api/v1")


@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "message": "PC Builder API is running"}


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)