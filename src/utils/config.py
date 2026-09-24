"""
Configuration loader for the Journal Entry Audit system.
Reads YAML configuration and merges with environment variables.
"""
import os
from pathlib import Path
from typing import Any, Dict
import yaml
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent
CONFIG_PATH = BASE_DIR / "config" / "config.yaml"

def load_config(config_file: Path = CONFIG_PATH) -> Dict[str, Any]:
    """
    Loads YAML configuration from disk and returns as a Python dictionary.
    """
    if not config_file.exists():
        raise FileNotFoundError(f"Configuration file not found at: {config_file}")
        
    with open(config_file, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
        
    # Override with environment variables if present
    if os.getenv("DATASET_ROWS"):
        config["dataset"]["rows"] = int(os.environ["DATASET_ROWS"])
    if os.getenv("RANDOM_SEED"):
        config["dataset"]["seed"] = int(os.environ["RANDOM_SEED"])
        
    return config
