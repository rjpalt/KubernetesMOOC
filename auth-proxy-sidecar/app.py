#!/usr/bin/env python3
"""
Azure Prometheus Authentication Sidecar
Simple token management and query proxy
"""

import json
import sys
import threading
import time
from datetime import datetime, timedelta

import requests
from azure.identity import DefaultAzureCredential
from flask import Flask, jsonify, request

app = Flask(__name__)


class TokenManager:
    def __init__(self):
        print("Initializing TokenManager...")
        try:
            self.credential = DefaultAzureCredential()
            print("DefaultAzureCredential initialized successfully")
        except Exception as e:
            print(f"CRITICAL: Failed to initialize DefaultAzureCredential: {e}")
            sys.exit(1)

        self.token = None
        self.expires_at = None
        self.lock = threading.Lock()

        # Try to get initial token - fail fast if this doesn't work
        try:
            self.refresh_token()
            print("Initial token acquired successfully")
        except Exception as e:
            print(f"CRITICAL: Failed to acquire initial Azure token: {e}")
            print("This sidecar cannot function without Azure authentication. Exiting.")
            sys.exit(1)

        # Start background refresh thread
        self.refresh_thread = threading.Thread(target=self._refresh_loop, daemon=True)
        self.refresh_thread.start()
        print("Background token refresh thread started")

    def _refresh_loop(self):
        """Background thread to refresh token every 30 minutes"""
        while True:
            time.sleep(1800)  # 30 minutes
            try:
                self.refresh_token()
                print(f"SUCCESS: Token refreshed at {datetime.now()}")
            except Exception as e:
                print(f"ERROR: Token refresh failed: {e}")
                print("This is a serious issue - authentication may fail soon!")
                # Don't exit here, let the app try to continue and fail on actual requests

    def refresh_token(self):
        """Refresh the Azure AD token"""
        with self.lock:
            try:
                print("Attempting to refresh Azure token...")
                token_response = self.credential.get_token("https://prometheus.monitor.azure.com/.default")

                if not token_response or not token_response.token:
                    raise ValueError("Token response was empty or invalid")

                self.token = token_response.token
                self.expires_at = datetime.now() + timedelta(seconds=token_response.expires_on - time.time())
                print(f"SUCCESS: New token acquired, expires at {self.expires_at}")

            except Exception as e:
                print(f"ERROR: Failed to acquire token: {e}")
                # Clear token on failure so health check shows the problem
                self.token = None
                self.expires_at = None
                raise

    def get_valid_token(self):
        """Get a valid token, refreshing if necessary"""
        with self.lock:
            # Check if we need to refresh (5 minutes before expiry)
            if self.expires_at and datetime.now() >= self.expires_at - timedelta(minutes=5):
                print("Token expiring soon, refreshing...")
                try:
                    self.refresh_token()
                except Exception as e:
                    print(f"ERROR: Failed to refresh expiring token: {e}")
                    # Don't return None here - let the caller try with the old token
                    # and get a proper HTTP error that can be debugged

            if not self.token:
                raise ValueError("No valid Azure token available")

            return self.token


# Initialize token manager globally - fail fast if Azure auth doesn't work
try:
    token_manager = TokenManager()
except Exception as e:
    print(f"CRITICAL: Failed to initialize token manager: {e}")
    sys.exit(1)


@app.route("/api/v1/query", methods=["POST"])
def proxy_query():
    """Proxy Prometheus queries to Azure with authentication"""
    try:
        # Get valid token - this will raise an exception if no token available
        token = token_manager.get_valid_token()

        # Extract query from form data
        query = request.form.get("query")
        if not query:
            print("ERROR: Missing query parameter in request")
            return jsonify({"error": "Missing query parameter"}), 400

        print(f"Proxying query: {query[:100]}...")  # Log first 100 chars for debugging

        # Forward to Azure Prometheus
        azure_url = "https://defaultazuremonitorworkspace-northeurope-fqbjcahubug7cdcv.northeurope.prometheus.monitor.azure.com/api/v1/query"
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/x-www-form-urlencoded"}
        data = {"query": query}

        response = requests.post(azure_url, headers=headers, data=data, timeout=30)

        print(f"Azure response status: {response.status_code}")

        # Check for authentication errors specifically
        if response.status_code == 401:
            print("ERROR: Azure returned 401 - token may be invalid")
            return jsonify({"error": "Authentication failed with Azure Prometheus"}), 401
        elif response.status_code == 403:
            print("ERROR: Azure returned 403 - insufficient permissions")
            return jsonify({"error": "Insufficient permissions for Azure Prometheus"}), 403

        # Try to parse JSON response
        try:
            response_data = response.json()
        except json.JSONDecodeError as e:
            print(f"ERROR: Failed to parse Azure response as JSON: {e}")
            print(f"Raw response: {response.text[:200]}...")
            return jsonify({"error": "Invalid JSON response from Azure Prometheus"}), 502

        return response_data, response.status_code

    except ValueError as e:
        print(f"ERROR: Token validation failed: {e}")
        return jsonify({"error": "Authentication token not available"}), 500
    except requests.exceptions.Timeout:
        print("ERROR: Timeout connecting to Azure Prometheus")
        return jsonify({"error": "Timeout connecting to Azure Prometheus"}), 504
    except requests.exceptions.ConnectionError as e:
        print(f"ERROR: Connection error to Azure Prometheus: {e}")
        return jsonify({"error": "Connection error to Azure Prometheus"}), 502
    except Exception as e:
        print(f"ERROR: Unexpected error in proxy_query: {e}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@app.route("/health")
def health():
    """Health check endpoint"""
    token_valid = token_manager.token is not None
    expires_at_str = token_manager.expires_at.isoformat() if token_manager.expires_at else None

    # Calculate time until expiry for easier debugging
    time_to_expiry = None
    if token_manager.expires_at:
        delta = token_manager.expires_at - datetime.now()
        time_to_expiry = str(delta)

    health_data = {
        "status": "healthy" if token_valid else "unhealthy",
        "token_valid": token_valid,
        "expires_at": expires_at_str,
        "time_to_expiry": time_to_expiry,
        "timestamp": datetime.now().isoformat(),
    }

    status_code = 200 if token_valid else 503

    if not token_valid:
        print("WARNING: Health check failed - no valid token available")

    return jsonify(health_data), status_code


if __name__ == "__main__":
    print("Starting Azure Prometheus Authentication Sidecar...")
    print("Health check available at: http://localhost:8080/health")
    print("Query proxy available at: http://localhost:8080/api/v1/query")
    app.run(host="0.0.0.0", port=8080, debug=False)
