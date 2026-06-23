"""
Entry point for the Zomato Restaurant Recommendation System API.
"""

import sys
from pathlib import Path

# Add project root to sys.path to ensure src module can be found
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import logging
import uvicorn

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s │ %(name)-30s │ %(levelname)-7s │ %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

def main() -> None:
    """Launch the FastAPI server."""
    logger.info("Starting FastAPI server via uvicorn...")
    
    import os
    port = int(os.environ.get("PORT", 8000))
    
    uvicorn.run(
        "src.api.routes:app",
        host="0.0.0.0",
        port=port,
        reload=True,
    )

if __name__ == "__main__":
    main()
