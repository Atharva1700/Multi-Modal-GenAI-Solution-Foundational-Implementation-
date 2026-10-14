#!/usr/bin/env python3
"""Multi-modal extraction: a text document and an image -> one merged JSON result.

Usage:
    export ANTHROPIC_API_KEY=...
    python main.py --text sample/report.txt --image sample/chart.png --out result.json
"""
import argparse
import base64
import json
import mimetypes
import os
from pathlib import Path

import anthropic

MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-5-5")
KEYS = '"title", "summary", "entities", "key_facts", "dates"'
SCHEMA = f"Return ONLY a JSON object with keys {KEYS}. Lists hold strings. No prose outside the JSON."


def parse_json_response(text: str) -> dict:
    """Parse a model reply that should be JSON, tolerating a ```json fence."""
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`").removeprefix("json").strip()
    return json.loads(text)


def ask(client: anthropic.Anthropic, content: list, instruction: str) -> dict:
    resp = client.messages.create(
        model=MODEL,
        max_tokens=2048,
        messages=[{"role": "user", "content": content + [{"type": "text", "text": instruction}]}],
    )
    return parse_json_response(resp.content[0].text)


def extract_text(client: anthropic.Anthropic, path: Path) -> dict:
    doc = path.read_text(encoding="utf-8")
    content = [{"type": "text", "text": f"<document>\n{doc}\n</document>"}]
    return ask(client, content, f"Extract structured information from the document above. {SCHEMA}")


def extract_image(client: anthropic.Anthropic, path: Path) -> dict:
    media_type = mimetypes.guess_type(path.name)[0] or "image/png"
    data = base64.standard_b64encode(path.read_bytes()).decode("ascii")
    content = [{"type": "image", "source": {"type": "base64", "media_type": media_type, "data": data}}]
    instruction = f"Extract structured information from this image. Put visible text in key_facts. {SCHEMA}"
    return ask(client, content, instruction)


def merge(client: anthropic.Anthropic, text_result: dict, image_result: dict) -> dict:
    """Combine two extractions into one coherent result, listing disagreements under 'conflicts'."""
    payload = json.dumps({"text_source": text_result, "image_source": image_result}, indent=2)
    instruction = (
        "Below are two extractions from related sources, a text document and an image.\n"
        f"{payload}\n\n"
        "Merge them into one coherent result. Remove duplicates. If the sources disagree, "
        f'record the disagreements in a "conflicts" list. {SCHEMA[:-len(" No prose outside the JSON.")]}, "conflicts".'
    )
    return ask(client, [], instruction)


def run(text_path: Path | None, image_path: Path | None) -> dict:
    if not text_path and not image_path:
        raise ValueError("Provide --text, --image, or both.")
    client = anthropic.Anthropic()
    text_result = extract_text(client, text_path) if text_path else None
    image_result = extract_image(client, image_path) if image_path else None
    if text_result and image_result:
        return merge(client, text_result, image_result)
    return text_result or image_result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--text", type=Path, help="Path to a .txt or .md document")
    parser.add_argument("--image", type=Path, help="Path to a PNG, JPEG, GIF or WebP image")
    parser.add_argument("--out", type=Path, help="Write JSON here instead of stdout")
    args = parser.parse_args()

    result = json.dumps(run(args.text, args.image), indent=2, ensure_ascii=False)
    if args.out:
        args.out.write_text(result + "\n", encoding="utf-8")
        print(f"Wrote {args.out}")
    else:
        print(result)


if __name__ == "__main__":
    main()
