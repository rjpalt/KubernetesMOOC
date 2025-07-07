import logging
import os
import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

logger = logging.getLogger(__name__)

app = FastAPI(title="Todo App", version="0.1.0")


@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Root endpoint - returns a simple HTML page."""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Todo App</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #333; text-align: center; }
            .status { background-color: #e8f5e8; padding: 10px; border-radius: 5px; margin: 20px 0; }
            .info { color: #666; font-size: 14px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Todo App</h1>
            <div class="status">
                <h3>✅ Application Status: Running</h3>
                <p>Your todo application is up and running successfully!</p>
            </div>
            <div class="info">
                <h4>Available Endpoints:</h4>
                <ul>
                    <li><code>/</code> - This page</li>
                    <li><code>/health</code> - Health check endpoint</li>
                </ul>
            </div>
        </div>
    </body>
    </html>
    """
    return html_content


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


def main():
    """Run the server."""
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"Server started in port {port}")

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False,  # Set to False for production
    )


if __name__ == "__main__":
    main()
