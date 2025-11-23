import os
import json

root = os.getcwd()
prompts_dir = os.path.join(root, "prompts")

def find_seed_base(base_name):
    for ext in ("png", "jpg", "jpeg", "webp"):
        rel = os.path.join("images", f"{base_name}.{ext}")
        if os.path.exists(os.path.join(root, rel)):
            return rel
    return None

def normalize_file(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        data = {}
    out = {}
    # id from filename
    fname = os.path.basename(path)
    num = fname[:4] if fname[:4].isdigit() else None
    if num:
        out["id"] = num
    # seed
    seed = data.get("seed")
    if seed and not os.path.exists(os.path.join(root, seed)):
        seed = None
    if not seed:
        seed = find_seed_base("02seed")
    if seed:
        out["seed"] = seed
    # tags array
    tags = data.get("tags")
    if isinstance(tags, list):
        out["tags"] = tags
    else:
        out["tags"] = []
    # write back
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

def main():
    for f in os.listdir(prompts_dir):
        if f.endswith(".tags.json") and f[:4].isdigit():
            normalize_file(os.path.join(prompts_dir, f))
    print("Done normalizing tags.json files.")

if __name__ == "__main__":
    main()
