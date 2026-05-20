from fastapi import FastAPI
from api.routes import router

# Create the main FastAPI application
app = FastAPI(
    title="Voice-Based Meeting Summarizer API",
    description="An API to transcribe, summarize, and generate audio summaries of meetings.",
    version="1.0.0"
)

# Include the routes from our api/routes.py file
# By keeping routes in a separate file, our code stays organized and modular.
app.include_router(router)

@app.get("/")
async def root():
    """
    A simple health-check endpoint to verify the API is running.
    """
    return {"message": "Welcome to the Voice-Based Meeting Summarizer API. Go to /docs to test the endpoints."}

if __name__ == "__main__":
    import uvicorn
    # This runs the server when you execute `python main.py` directly.
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
