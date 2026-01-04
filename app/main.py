import logging
import time
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

logger = logging.getLogger("trashlight")

logger.info("Trashlight service started")

while True:
    logger.info("Hello World from Trashlight 🚀")
    time.sleep(10)
