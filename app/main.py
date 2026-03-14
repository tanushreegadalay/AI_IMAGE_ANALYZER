"""FastAPI application entry point."""

import logging

from fastapi import FastAPI

from app.api.routes import router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

app = FastAPI(
    title="AI Image Analyzer API",
    description="Upload an image and get AI-driven analysis from vision LLMs.",
    version="1.0.0",
)
app.include_router(router)
