from dotenv import load_dotenv
load_dotenv()

import os
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

# CORS — load from env or default to Next.js dev server
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(components_router, prefix="/api/v1")
app.include_router(builds_router, prefix="/api/v1")


@app.get("/", tags=["Health"])
def health_check() -> dict[str, str]:
    return {"status": "ok", "message": "PC Builder API is running"}


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)