from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from auth.jwt_handler import JWTBearer
from services.conversation_service import ConversationService
from services.ai_service import AIService
import os
import logging
from datetime import datetime

load_dotenv()

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with allowed origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

conversation_service = ConversationService()
ai_service = AIService()

@app.get("/")
async def root():
    return {"message": "Welcome to the Coding Assistant API"}

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring and container orchestration"""
    try:
        # Check MongoDB connection
        conversation_service.get_user_conversations("health_check")
        
        # Check if AI model is loaded
        if not ai_service.model:
            return {
                "status": "warning",
                "message": "AI model not loaded properly"
            }
        
        return {
            "status": "ok",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

# Additional routes and logic for conversations and AI service will go here

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)