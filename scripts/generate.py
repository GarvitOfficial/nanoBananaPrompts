import os
import sys
import json
import base64
import urllib.request

root = os.getcwd()
images_dir = os.path.join(root, "images")
prompts_dir = os.path.join(root, "prompts")

def ensure_dirs():
    os.makedirs(images_dir, exist_ok=True)
    os.makedirs(prompts_dir, exist_ok=True)

def zero_pad(n, width=4):
    s = str(n)
    return s if len(s) >= width else ("0" * (width - len(s))) + s

def list_existing_numbers():
    a = []
    b = []
    if os.path.exists(images_dir):
        for f in os.listdir(images_dir):
            if len(f) >= 8 and f[:4].isdigit() and f[4] == ".":
                a.append(int(f[:4]))
    if os.path.exists(prompts_dir):
        for f in os.listdir(prompts_dir):
            if len(f) == 8 and f.endswith(".txt") and f[:4].isdigit():
                b.append(int(f[:4]))
    return sorted(list(set(a + b)))

def next_number():
    nums = list_existing_numbers()
    return (nums[-1] + 1) if nums else 1

banned = [
    "nudity",
    "nude",
    "nsfw",
    "violence",
    "gore",
    "blood",
    "weapon",
    "gun",
    "knife",
    "hate",
    "racist",
    "sex",
    "explicit",
    "real person",
    "celebrity",
    "trademark",
    "copyright",
    "logo",
    "brand"
]

def sanitize_subject(input_str):
    s = (input_str or "").strip()
    if not s:
        return ""
    lower = s.lower()
    for w in banned:
        if w in lower:
            return ""
    return s

def build_prompt(subject):
    detail = [
        "high-quality cinematic illustration",
        "soft natural lighting",
        "vivid yet balanced color palette",
        "clean composition",
        "tasteful, family-friendly aesthetic",
        "original concept"
    ]
    return subject + ", " + ", ".join(detail)

def build_tags(subject):
    s = subject.lower()
    cleaned = "".join(ch if (ch.isalnum() or ch.isspace() or ch == "-") else " " for ch in s)
    base = [t for t in cleaned.split() if t]
    extras = ["illustration", "family-friendly", "original", "ai-art", "clean"]
    seen = []
    for x in base[:5] + extras:
        if len(x) > 2 and x not in seen:
            seen.append(x)
    if len(seen) < 3:
        for x in ["art", "scene", "design"]:
            if x not in seen:
                seen.append(x)
    return seen[:8]

def write_prompt_file(number, prompt):
    p = os.path.join(prompts_dir, f"{number}.txt")
    with open(p, "w", encoding="utf-8") as f:
        f.write(prompt)
    return p

def write_tags_file(number, tags):
    p = os.path.join(prompts_dir, f"{number}.tags.json")
    with open(p, "w", encoding="utf-8") as f:
        json.dump(tags, f, indent=2)
    return p

def generate_with_openai(prompt, size):
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        return None
    body = json.dumps({
        "model": "gpt-image-1",
        "prompt": prompt,
        "size": size or "1024x1024",
        "response_format": "b64_json"
    }).encode("utf-8")
    req = urllib.request.Request(
        url="https://api.openai.com/v1/images/generations",
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {key}"
        },
        method="POST"
    )
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            img = data.get("data", [{}])[0].get("b64_json")
            return img
    except Exception:
        return None

def save_base64_jpeg(base64_data, out_path):
    buf = base64.b64decode(base64_data)
    with open(out_path, "wb") as f:
        f.write(buf)

def main():
    ensure_dirs()
    argv = sys.argv[1:]
    seed = None
    parts = []
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--seed":
            if i + 1 < len(argv):
                seed = argv[i + 1]
                i += 2
                continue
            else:
                i += 1
                continue
        if a.startswith("--seed="):
            seed = a.split("=", 1)[1]
            i += 1
            continue
        parts.append(a)
        i += 1
    subject = sanitize_subject(" ".join(parts))
    if not subject:
        try:
            entered = input("Subject: ").strip()
        except EOFError:
            entered = ""
        subject = sanitize_subject(entered)
        if not subject:
            subject = "original AI-generated scene"
    prompt = build_prompt(subject)
    tag_list = build_tags(subject)
    n = zero_pad(next_number())
    prompt_path = write_prompt_file(n, prompt)
    tags_obj = {"tags": tag_list}
    if seed:
        seed_path = seed
        if not os.path.isabs(seed_path):
            seed_path = os.path.normpath(seed_path)
        abs_seed = seed_path if os.path.isabs(seed_path) else os.path.join(root, seed_path)
        if os.path.exists(abs_seed):
            rel = os.path.relpath(abs_seed, root)
            tags_obj["seed"] = rel.replace("\\", "/")
    write_tags_file(n, tags_obj)
    base64_img = generate_with_openai(prompt, "1024x1024")
    if not base64_img:
        sys.stderr.write("Image provider not configured. Skipping image generation.\n")
        sys.stderr.write("Set OPENAI_API_KEY to enable generation.\n")
        sys.stdout.write(f"Prompt: prompts/{n}.txt\n")
        sys.stdout.write(f"Tags: {', '.join(tag_list)}\n")
        sys.exit(2)
    image_path = os.path.join(images_dir, f"{n}.jpg")
    save_base64_jpeg(base64_img, image_path)
    sys.stdout.write(f"Image: images/{n}.jpg\n")
    sys.stdout.write(f"Prompt: prompts/{n}.txt\n")
    sys.stdout.write(f"Tags: {', '.join(tag_list)}\n")

if __name__ == "__main__":
    main()
