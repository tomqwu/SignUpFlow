"""Tests for verifying locale keys exist in translation files."""
import pytest
import json
import os
import re
from pathlib import Path

def get_frontend_files():
    """Get all HTML and JS files in the frontend directory."""
    frontend_dir = Path("/home/ubuntu/SignUpFlow/frontend")
    files = []
    for ext in ["*.html", "*.js"]:
        for file in frontend_dir.rglob(ext):
            if "tests/" not in str(file):
                files.append(file)
    return files

def extract_keys_from_file(file_path):
    """Extract i18n keys from a file."""
    content = file_path.read_text()
    keys = set()
    
    # Match data-i18n="key"
    data_i18n_matches = re.findall(r'data-i18n=["\']([^"\']+)["\']', content)
    keys.update(data_i18n_matches)
    
    # Match i18n.t("key") or i18n.t('key')
    # Note: This is a simple regex and might miss complex cases or variables
    js_i18n_matches = re.findall(r'i18n\.t\(["\']([^"\']+)["\']\)', content)
    keys.update(js_i18n_matches)
    
    return keys

def load_locale_keys(locale_file):
    """Load keys from a JSON locale file, flattening nested objects."""
    with open(locale_file, 'r') as f:
        data = json.load(f)
    
    def flatten(obj, prefix=""):
        keys = set()
        for k, v in obj.items():
            full_key = f"{prefix}.{k}" if prefix else k
            if isinstance(v, dict):
                keys.update(flatten(v, full_key))
            else:
                keys.add(full_key)
        return keys
    
    return flatten(data)

def test_all_keys_exist_in_en_locales():
    """Verify that all keys used in frontend files exist in English locale files."""
    frontend_files = get_frontend_files()
    used_keys = set()
    for file_path in frontend_files:
        used_keys.update(extract_keys_from_file(file_path))
    
    # Load all locale files
    locale_dir = Path("/home/ubuntu/SignUpFlow/locales/en")
    defined_keys = set()
    
    # Map prefixes to files (convention based)
    # e.g. "admin.title" -> admin.json
    # "schedule.upcoming" -> schedule.json
    # "common.save" -> common.json
    # Some keys might be in common.json but used without prefix? No, usually namespaced.
    
    # Let's load all keys from all files into a single set with their namespaces
    # Actually, the keys in the code usually include the namespace if the file structure implies it.
    # But wait, the locale loader in the app might merge them.
    # Let's assume the app merges them or they are namespaced.
    # Looking at usage: data-i18n="admin.team_management" -> admin.json: { "team_management": ... }
    # So "admin" is the namespace/filename.
    
    # Let's build a map of available keys
    available_keys = set()
    
    for locale_file in locale_dir.glob("*.json"):
        namespace = locale_file.stem # e.g. "admin"
        file_keys = load_locale_keys(locale_file)
        
        # Add keys prefixed with namespace
        for key in file_keys:
            available_keys.add(f"{namespace}.{key}")
            
            # Also add keys without prefix if they are in common? 
            # Or maybe the app allows "title" from "admin.json" if loaded in admin context?
            # The usage seems to be explicit: "admin.team_management".
            # But "common.back" might be used as "back" if common is global?
            # Let's check usage patterns.
            
    # Filter out dynamic keys (containing ${} or similar)
    static_keys = {k for k in used_keys if not re.search(r'\$\{.*\}|\+', k)}
    
    missing_keys = []
    for key in static_keys:
        # Ignore keys that are likely dynamic or constructed at runtime if not found
        if key not in available_keys:
            # Check if it exists in common without prefix?
            # Or check if it's a known dynamic pattern we missed
            missing_keys.append(key)
            
    # Assert no missing keys
    # We might have false positives, so we can whitelist known issues or improve regex
    # For now, let's print them and fail if any
    
    assert not missing_keys, f"Missing translation keys: {missing_keys}"

if __name__ == "__main__":
    # Manual run for debugging
    try:
        test_all_keys_exist_in_en_locales()
        print("All keys found!")
    except AssertionError as e:
        print(e)
