"""Cache utility for extraction results."""

import json
from pathlib import Path
from typing import Any, Optional, Dict

from logger import get_logger

log = get_logger(__name__)


def get_cache_file_path(job_file: Path, cache_dir: str = "data/extracted") -> Path:
    """Get the JSON cache file path for a job file."""
    cache_directory = Path(cache_dir)
    cache_directory.mkdir(parents=True, exist_ok=True)
    return cache_directory / f"{job_file.stem}.json"


def load_extraction_cache(job_file: Path) -> Dict:
    """Load extraction results from JSON cache file."""
    cache_file = get_cache_file_path(job_file)
    
    if cache_file.exists():
        try:
            with open(cache_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            log.warning(f"Failed to load cache file {cache_file}: {e}")
    
    return {}


def save_extraction_result(job_file: Path, workflow_name: str, result: Any):
    """Save extraction result to JSON cache file."""
    cache_file = get_cache_file_path(job_file)
    cache_data = load_extraction_cache(job_file)
    
    cache_data[workflow_name] = result
    
    try:
        with open(cache_file, 'w') as f:
            json.dump(cache_data, f, indent=2)
        log.info(f"Saved {workflow_name} result for {job_file.name}")
    except Exception as e:
        log.error(f"Failed to save cache file {cache_file}: {e}")


def is_extraction_cached(job_file: Path, workflow_name: str) -> bool:
    """Check if extraction result already exists."""
    cache_data = load_extraction_cache(job_file)
    return workflow_name in cache_data


def get_cached_extraction(job_file: Path, workflow_name: str) -> Optional[Any]:
    """Get cached extraction result."""
    cache_data = load_extraction_cache(job_file)
    return cache_data.get(workflow_name)