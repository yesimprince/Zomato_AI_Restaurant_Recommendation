"""
Pre-download and cache the Zomato dataset during the build phase.

This script runs during `railway build` so the parquet cache is baked
into the deployed image. At runtime the server reads the cache instantly
instead of downloading ~52K rows from Hugging Face (which can OOM on
limited-memory containers).
"""

import sys
from pathlib import Path

# Ensure project root is on sys.path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.config import settings
from src.data.loader import DatasetLoader


def main() -> None:
    print(f"[preload] Downloading dataset '{settings.hf_dataset_name}' …")
    loader = DatasetLoader()
    df = loader.load()
    print(f"[preload] Dataset cached — {len(df)} rows, columns: {list(df.columns)}")


if __name__ == "__main__":
    main()
