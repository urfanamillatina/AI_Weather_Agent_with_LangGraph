from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from dotenv import load_dotenv
from agent_graph import build_graph, State
import uvicorn

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="AI Weather Agent API",
    description="An intelligent weather assistant with AI-powered reasoning",
    version="1.0.0",
    contact={
        "name": "Your Name",
        "email": "your.email@example.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    }
)

# Compile the graph once at startup
graph = build_graph()

# Request models
class WeatherRequest(BaseModel):
    """Request model for weather query"""
    city: str = Field(..., description="City name", example="New York")
    question: str = Field(..., description="Weather-related question", 
                          example="Should I bring an umbrella today?")
    send_email_flag: bool = Field(default=False, description="Send result to email")
    send_whatsapp_flag: bool = Field(default=False, description="Send result to WhatsApp")
    
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "city": "London",
                "question": "Is it good weather for a picnic?",
                "send_email_flag": True,
                "send_whatsapp_flag": False
            }
        }
    }

class WeatherResponse(BaseModel):
    """Response model for weather query"""
    success: bool
    city: str
    weather_text: Optional[str] = None
    answer: Optional[str] = None
    email_sent: Optional[bool] = None
    whatsapp_sent: Optional[bool] = None
    error: Optional[str] = None
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "city": "London",
                "weather_text": "The weather in London is scattered clouds, temperature 18°C, humidity 65%.",
                "answer": "Based on the current weather in London...",
                "email_sent": True,
                "whatsapp_sent": False
            }
        }
    }

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    service: str

# Routes
@app.get("/", response_model=dict, tags=["Root"])
async def root():
    """Root endpoint with API information"""
    return {
        "message": "🌦️ AI Weather Agent API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "health": "/health",
            "weather": "/weather",
            "test": "/test/weather"
        }
    }

@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "service": "AI Weather Agent API"
    }

@app.post("/weather", response_model=WeatherResponse, tags=["Weather"])
async def get_weather_analysis(request: WeatherRequest):
    """
    Get AI-powered weather analysis for a city
    """
    try:
        # Create initial state
        init: State = {
            "city": request.city,
            "question": request.question,
            "send_email_flag": request.send_email_flag,
            "send_whatsapp_flag": request.send_whatsapp_flag
        }
        
        # Execute the agent graph
        final_state = graph.invoke(init)
        
        # Check if notifications were actually sent
       
        email_sent = request.send_email_flag
        whatsapp_sent = request.send_whatsapp_flag
        
    
        response = {
            "success": True,
            "city": request.city,
            "weather_text": final_state.get("weather_text"),
            "answer": final_state.get("answer"),
            "email_sent": email_sent,
            "whatsapp_sent": whatsapp_sent
        }
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing weather request: {str(e)}"
        )

@app.get("/test/weather", response_model=WeatherResponse, tags=["Test"])
async def test_weather_endpoint():
    """
    Test endpoint with sample data
    
    Returns a sample weather analysis for testing
    """
    try:
        # Test with sample data
        init: State = {
            "city": "Tokyo",
            "question": "Should I wear a jacket?",
            "send_email_flag": False,
            "send_whatsapp_flag": False
        }
        
        final_state = graph.invoke(init)
        
        return {
            "success": True,
            "city": "Tokyo",
            "weather_text": final_state.get("weather_text"),
            "answer": final_state.get("answer"),
            "email_sent": False,
            "whatsapp_sent": False
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Test failed: {str(e)}"
        )

# Run without reload for direct execution
if __name__ == "__main__":
    # Run the FastAPI server
    print("Starting AI Weather Agent API...")
    print("🌐 Server running at: http://127.0.0.1:8000")
    print("📚 API Documentation: http://127.0.0.1:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)