#!/usr/bin/env python3

import time
import uuid
import logging
from datetime import datetime, timezone

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)

def main():
    # Generate a random string on startup and store it in memory
    random_string = str(uuid.uuid4())
    logger.info(f"Application started. Generated string: {random_string}")
    
    # Output the string every 5 seconds with timestamp
    while True:
        timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
        logger.info(f"{timestamp}: {random_string}")
        time.sleep(5)

if __name__ == "__main__":
    main()
