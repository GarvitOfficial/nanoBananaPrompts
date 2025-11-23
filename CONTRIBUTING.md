# Contributing

## Overview
- Keep content safe and family‑friendly: no nudity, violence, hate, real people, brands/logos, or copyrighted/trademarked characters.
- Each dataset entry comprises an image, a prompt text, and a minimal tags JSON.

## File Structure
- Images: `images/####.<ext>` where `<ext>` is one of `png`, `jpg`, `jpeg`, `webp`.
- Prompt: `prompts/####.txt` containing the full text prompt.
- Tags JSON: `prompts/####.tags.json` with only `id`, `seed`, and optional `tags`.

Example `prompts/0007.tags.json`:
```json
{
  "id": "0007",
  "seed": "images/02seed.png",
  "tags": ["cinematic", "portrait", "soft-light"]
}
```

## Adding a New Entry
- Pick the next number not already used (e.g., `0008`).
- Save your prompt to `prompts/0008.txt`.
- Place your image at `images/0008.<ext>` (`png/jpg/jpeg/webp`).
- Create `prompts/0008.tags.json` with:
  - `id`: the entry number as a 4‑digit string
  - `seed`: path to a seed image under `images/` (see Seed Handling)
  - `tags`: optional list of 3–8 keywords

## Seed Handling
- Preferred: set an explicit seed path in the tags JSON, e.g. `"seed": "images/01seed.png"`.
- If you don’t set a seed, a default seed `images/02seed.*` will be used if present. Supported extensions: `png`, `jpg`, `jpeg`, `webp`.
- To introduce a new default seed, add one of `images/02seed.png|jpg|jpeg|webp`. Detection automatically picks the available format.

## JSON Schema
- Minimal, strict:
  - `id`: 4‑digit string matching the file number
  - `seed`: relative path under `images/`
  - `tags`: optional array of keywords (empty array allowed)
- Do not include `prompt` or `caption` in JSON; the full prompt lives in `prompts/####.txt`.

## Quality Guidelines
- Use descriptive, professional prompts; avoid sensitive terms.
- Keep images original (AI‑generated), not real persons.
- Ensure images render well at typical table width; avoid extreme aspect ratios.

## PR Checklist
- Files added: `images/####.<ext>`, `prompts/####.tags.json`.
- Confirm tags JSON contains only `id`, `seed`, `tags`.
- No secrets or API keys committed.

## Notes
- Seed detection supports `png`, `jpg`, `jpeg`, `webp`.
