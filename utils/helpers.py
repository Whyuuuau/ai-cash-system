"""
Helper utilities for the 72-Hour AI Cash System
"""
import json
import yaml
import os
from pathlib import Path
from datetime import datetime, timedelta

def load_config(config_path="config/config.yaml"):
    """Load YAML configuration file"""
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def load_niches(niches_path="config/niches.json"):
    """Load niche configurations"""
    with open(niches_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(data, filepath):
    """Save data as JSON"""
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_json(filepath):
    """Load JSON data"""
    if not os.path.exists(filepath):
        return {}
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_time_remaining(start_time, duration_hours=72):
    """Calculate time remaining in the challenge"""
    deadline = start_time + timedelta(hours=duration_hours)
    remaining = deadline - datetime.now()
    return {
        'deadline': deadline,
        'remaining_seconds': remaining.total_seconds(),
        'remaining_hours': remaining.total_seconds() / 3600,
        'remaining_minutes': remaining.total_seconds() / 60,
        'is_expired': remaining.total_seconds() <= 0
    }

def format_currency(amount):
    """Format amount as currency"""
    return f"${amount:,.2f}"

def sanitize_filename(filename):
    """Sanitize filename for safe file operations"""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename

def create_product_url_mapping(niches, base_url="https://gumroad.com/l/"):
    """Create product URL mapping"""
    mapping = {}
    for niche in niches:
        mapping[niche] = f"{base_url}{sanitize_filename(niche)}"
    return mapping

def calculate_progress(current, target):
    """Calculate progress percentage"""
    if target == 0:
        return 0
    return (current / target) * 100

def get_env_variable(key, default=None):
    """Get environment variable with fallback"""
    from dotenv import load_dotenv
    load_dotenv()
    return os.getenv(key, default)
