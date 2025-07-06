import logging
import os
import uvicorn
from fastapi import FastAPI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

logger = logging.getLogger(__name__)

app = FastAPI(title="Todo App", version="0.1.0")


@app.get("/")
async def read_root():
    """Root endpoint - just returns a simple message."""
    return {"message": "Todo App is running"}


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
