from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent.parent
kb_file = ROOT / "data" / "style_knowledge.json"

if __name__ == "__main__":
    data = json.loads(kb_file.read_text(encoding="utf-8"))
    print(f"Loaded {len(data)} style entries from {kb_file}")
    for item in data:
        print(f"- {item['style']}")

