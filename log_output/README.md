# Log Output App

## How to Run Locally

1. Install dependencies (if you haven't already):

   ```bash
   uv add fastapi uvicorn
   ```

2. Start the application:

   ```bash
   uv run app.py
   ```

3. Access the status endpoint in your browser or with curl:

   - [http://localhost:8000/](http://localhost:8000/)  (status)
   - [http://localhost:8000/health](http://localhost:8000/health)  (health check)

## How to Build a Docker Image

1. Build the Docker image with your chosen tag:

   ```bash
   ./build.sh log-output-app:<tag>
   # Example:
   ./build.sh log-output-app:v1.0
   ```

2. Run the Docker image:

   ```bash
   docker run -p 8000:8000 log-output-app:<tag>
   ```

If you can't manage this, maybe computers aren't for you.
