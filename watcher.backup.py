import os
import time
import json
import re
import requests
from pymongo import MongoClient
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from dotenv import load_dotenv

# -----------------------------
# Load configuration from .env
# -----------------------------
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
AI_ENDPOINT = os.getenv("AI_ENDPOINT")  # e.g., http://localhost:11434/api/generate
MODEL_NAME = os.getenv("MODEL_NAME")

# -----------------------------
# Connect to MongoDB
# -----------------------------
client = MongoClient(MONGO_URI)
db = client.get_database()        # Uses DB name from URI
collection = db.notes             # Default collection (change if needed)

# -----------------------------
# JSON extraction helpers
# These functions try to safely pull valid JSON blocks
# from AI responses, even if wrapped in code fences or malformed.
# -----------------------------
def strip_code_fences(text: str) -> str:
    """Remove Markdown-style ```json fences if present."""
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)```", text, re.IGNORECASE)
    return fence.group(1).strip() if fence else text

def extract_balanced_block(text: str, open_ch: str, close_ch: str):
    """Extract the first balanced {...} or [...] block from text."""
    start = text.find(open_ch)
    if start == -1:
        return None
    depth, in_str, esc, quote = 0, False, False, None
    for i, ch in enumerate(text[start:], start):
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == quote:
                in_str = False
        else:
            if ch in ('"', "'"):
                in_str, quote = True, ch
            elif ch == open_ch:
                depth += 1
            elif ch == close_ch:
                depth -= 1
                if depth == 0:
                    return text[start:i+1]
    return None

def extract_first_json(text: str):
    """Try to extract either a JSON array or object from text."""
    cleaned = strip_code_fences(text).lstrip()
    return extract_balanced_block(cleaned, "[", "]") or extract_balanced_block(cleaned, "{", "}")

# -----------------------------
# Core processing function
# -----------------------------
def process_text(text, filename, max_retries=1):
    """
    Send text to the AI model, request structured JSON output,
    validate/repair if needed, and insert results into MongoDB.
    """
    # Instruction prompt for the AI
    prompt_text = (
        "Split the following text into sections by topic.\n"
        "Return a JSON array of objects with fields: "
        "title (string), summary (string), tags (array of strings), content (string).\n"
        "If a value is missing, use an empty string or empty array.\n\n"
        f"TEXT:\n{text}"
    )

    # JSON Schema to enforce structure
    schema = {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "title":   {"type": "string"},
                "summary": {"type": "string"},
                "tags":    {"type": "array", "items": {"type": "string"}},
                "content": {"type": "string"},
            },
            "required": ["title", "summary", "tags", "content"],
            "additionalProperties": False
        }
    }

    def call_model(prompt, fix_mode=False):
        """Send request to AI endpoint, optionally in 'fix mode' to repair JSON."""
        payload = {
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False,
            "format": schema,   # Enforce schema
            "options": {"temperature": 0.0, "num_ctx": 8192}
        }
        if fix_mode:
            payload["prompt"] = (
                "Fix the following so it becomes valid JSON matching this schema exactly. "
                "Output JSON only, no explanations.\n\n"
                f"SCHEMA:\n{json.dumps(schema)}\n\n"
                f"DATA:\n{prompt}"
            )
        resp = requests.post(AI_ENDPOINT, json=payload, timeout=120)
        resp.raise_for_status()
        return (resp.json().get("response") or "").strip()

    # First attempt
    raw = call_model(prompt_text)

    # Retry loop for JSON parsing
    for attempt in range(max_retries + 1):
        candidate = extract_first_json(raw) or raw.strip()
        try:
            sections = json.loads(candidate)
            if not isinstance(sections, list):
                sections = [sections]
            break
        except json.JSONDecodeError as e:
            if attempt < max_retries:
                print(f"[WARN] JSON parse failed for {filename}, retrying schema-fix ({attempt+1}/{max_retries})...")
                raw = call_model(candidate, fix_mode=True)
            else:
                print(f"[ERROR] Failed to parse AI JSON for {filename}: {e}")
                print("Raw AI output (truncated):", (raw[:2000] + '...') if len(raw) > 2000 else raw)
                return

    # Insert structured sections into MongoDB
    for section in sections:
        collection.insert_one({
            "filename": filename,
            "title": section.get("title", ""),
            "summary": section.get("summary", ""),
            "tags": section.get("tags", []),
            "original": section.get("content", ""),
            "timestamp": time.time()
        })

    print(f"[INFO] Processed {filename} into {len(sections)} sections.")

# -----------------------------
# Watchdog event handler
# -----------------------------
class Handler(FileSystemEventHandler):
    """Triggered when new files appear in the watched directory."""
    def on_created(self, event):
        if event.is_directory:
            return
        if event.src_path.lower().endswith(".txt"):
            filename = os.path.basename(event.src_path)
            try:
                with open(event.src_path, "r", encoding="utf-8") as f:
                    text = f.read()
                process_text(text, filename)
            except Exception as e:
                print(f"[ERROR] Failed to process {filename}: {e}")

# -----------------------------
# Main loop
# -----------------------------
if __name__ == "__main__":
    path = "/mnt/storage"  # Directory to watch
    event_handler = Handler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=False)
    observer.start()
    print(f"[INFO] Note-watcher is running. Watching '{path}' for new .txt files using model '{MODEL_NAME}'...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

