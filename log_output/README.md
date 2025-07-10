# Log Output App - Multi-Container

## How to Run Locally

1. Install all dependencies from `pyproject.toml` and `uv.lock`:

   ```bash
   uv install
   ```

2. Start the generator application:

   ```bash
   uv run app.py
   ```

3. Start the log server application (in another terminal):

   ```bash
   uv run log_server.py
   ```

4. Access the endpoints in your browser or with curl:

   - [http://localhost:8000/](http://localhost:8000/)  (generator status)
   - [http://localhost:8000/health](http://localhost:8000/health)  (generator health)
   - [http://localhost:8001/logs](http://localhost:8001/logs)  (log server: log file contents)
   - [http://localhost:8001/health](http://localhost:8001/health)  (log server health)

## How to Build Docker Images

1. Build both Docker images with your chosen tag (default is `latest`):

   ```bash
   ./build.sh 1.10
   # or just ./build.sh for latest
   ```

   This builds:
   - `log-generator:1.10`
   - `log-server:1.10`

2. Run the containers together (recommended: use Docker Compose for shared volume testing)

   See the provided docker-compose.yml example in the project for details.

## How to Import Images to k3d and Deploy to Kubernetes

1. Import images to your k3d cluster:

   ```bash
   k3d image import log-generator:1.10 -c <your-cluster-name>
   k3d image import log-server:1.10 -c <your-cluster-name>
   ```

2. Deploy the application:

   ```bash
   kubectl apply -f manifests/
   ```

## Endpoints

- Generator:
  - `GET /` - Status
  - `GET /health` - Health check
- Log Server:
  - `GET /logs` - Log file contents
  - `GET /health` - Health check
  - `GET /status` - Log file stats

If you can't manage this, maybe computers aren't for you.
