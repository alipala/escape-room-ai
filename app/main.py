import os
from fastapi import FastAPI
from dotenv import load_dotenv
from .routes import game, user
from .utils.database import engine, Base
from .utils.logger import setup_logger

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(title="AI-Enhanced Escape Room Game")

# Set up logging
logger = setup_logger()

# Create database tables
Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(game.router)
app.include_router(user.router)

@app.on_event("startup")
async def startup_event():
    logger.info("Application starting up...")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutting down...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)