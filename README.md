# Multi-Modal GenAI Solution

A foundational multi-modal pipeline built on the Claude API. It takes a text
document and an image, extracts structured information from each, and merges
both into one JSON result. Any disagreements between the two sources are listed
under `conflicts`.

## How it works

1. **Text component**: sends the document to Claude and returns structured JSON.
2. **Image component**: sends the image to Claude (vision) and returns structured JSON.
3. **Merge**: a third call combines both extractions, removes duplicates, and records conflicts.

Either input can be used alone; the merge step runs only when both are given.

## Setup

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=your-key-here
```

Optional: set `CLAUDE_MODEL` to override the default model.

## Usage

```bash
python main.py --text sample/report.txt --image sample/chart.png --out result.json
```

Supply your own `sample/chart.png` (PNG, JPEG, GIF or WebP). Omit `--out` to print to stdout.

## Tests

The tests cover JSON parsing only and do not call the API:

```bash
python -m unittest discover -s tests -t .
```

## Output shape

```json
{
  "title": "...",
  "summary": "...",
  "entities": ["..."],
  "key_facts": ["..."],
  "dates": ["..."],
  "conflicts": ["..."]
}
```

`conflicts` appears only in merged output.
