import os
import sys
import json
import time

root = os.getcwd()
images_dir = os.path.join(root, "images")
prompts_dir = os.path.join(root, "prompts")
readme_path = os.path.join(root, "README.md")

def ensure_dirs():
    os.makedirs(images_dir, exist_ok=True)
    os.makedirs(prompts_dir, exist_ok=True)

def collect_entries():
    ensure_dirs()
    img_files = []
    for f in os.listdir(images_dir):
        if len(f) >= 8 and f[:4].isdigit() and f[4] == ".":
            img_files.append((f[:4], f))
    prompt_files = []
    for f in os.listdir(prompts_dir):
        if len(f) == 8 and f.endswith(".txt") and f[:4].isdigit():
            prompt_files.append((f[:4], f))
    tags_files = []
    for f in os.listdir(prompts_dir):
        if f.endswith(".tags.json") and f[:4].isdigit():
            tags_files.append((f[:4], f))
    by_num = {}
    for n, pf in prompt_files:
        by_num[n] = {"num": n, "promptFile": pf}
    for n, im in img_files:
        by_num.setdefault(n, {"num": n})["image"] = im
    for n, tf in tags_files:
        by_num.setdefault(n, {"num": n})["tagsFile"] = tf
    return [by_num[k] for k in sorted(by_num.keys())]

def safe_read(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return ""

def find_seed_base(base_name):
    for ext in ("png", "jpg", "jpeg", "webp"):
        rel = os.path.join("images", f"{base_name}.{ext}")
        if os.path.exists(os.path.join(root, rel)):
            return rel
    return None

def build_table(entries):
    rows_html = []
    for e in entries:
        pf = e.get("promptFile", "")
        prompt_full = safe_read(os.path.join(prompts_dir, pf)).replace("\n", " ")
        preview = first_three_words(prompt_full)
        prompt_link = f"<a href=\"prompts/{pf}\">See</a>" if pf else ""
        prompt_text = (preview + " … ") + prompt_link if preview else prompt_link
        tags_json = safe_read(os.path.join(prompts_dir, e.get("tagsFile", "")))
        seed_rel = None
        try:
            parsed = json.loads(tags_json)
            seed_rel = parsed.get("seed")
        except Exception:
            pass
        if seed_rel and not os.path.exists(os.path.join(root, seed_rel)):
            seed_rel = None
        if not seed_rel:
            seed_rel = find_seed_base("02seed")
        seed_cell = ""
        if seed_rel:
            abs_seed = os.path.join(root, seed_rel)
            if os.path.exists(abs_seed):
                seed_cell = f"<a href=\"{seed_rel}\"><img src=\"{seed_rel}\" alt=\"seed {e['num']}\" style=\"max-width:100%;height:auto;display:block;\"/></a>"
        img_cell = ""
        if e.get("image"):
            img_path = f"images/{e['image']}"
            img_cell = f"<a href=\"{img_path}\"><img src=\"{img_path}\" alt=\"{e['num']}\" style=\"max-width:100%;height:auto;display:block;\"/></a>"
        row = (
            "<tr>"
            f"<td style=\"width:6%;\">{e['num']}</td>"
            f"<td style=\"width:32%;\">{seed_cell}</td>"
            f"<td style=\"width:32%;\">{img_cell}</td>"
            f"<td style=\"width:30%;\">{prompt_text}</td>"
            "</tr>"
        )
        rows_html.append(row)
    table_html = (
        "<table style=\"width:100%;table-layout:fixed;\">"
        "<thead><tr>"
        "<th style=\"width:6%;\">#</th>"
        "<th style=\"width:32%;\">Seed</th>"
        "<th style=\"width:32%;\">Image</th>"
        "<th style=\"width:30%;\">Prompt</th>"
        "</tr></thead>"
        f"<tbody>{''.join(rows_html)}</tbody>"
        "</table>"
    )
    return table_html

def build_readme(entries):
    description = ""
    table = build_table(entries)
    lines = [
        "# Nano Banana Prompts",
        "",
        description,
        "",
        table
    ]
    return "\n".join(lines)

def build_mobile_gallery(entries):
    blocks = []
    for e in entries:
        num = e.get("num", "")
        pf = e.get("promptFile", "")
        prompt_link = f"[See](prompts/{pf})" if pf else ""
        tags_json = safe_read(os.path.join(prompts_dir, e.get("tagsFile", "")))
        title = None
        seed_rel = None
        try:
            parsed = json.loads(tags_json)
            title = parsed.get("title")
            seed_rel = parsed.get("seed")
        except Exception:
            pass
        if not title:
            prompt_text_full = safe_read(os.path.join(prompts_dir, pf)).replace("\n", " ")
            title = derive_title(prompt_text_full)
        seed_img = ""
        if seed_rel:
            abs_seed = os.path.join(root, seed_rel)
            if os.path.exists(abs_seed):
                seed_img = f"[![seed {num}]({seed_rel})]({seed_rel})"
        gen_img = ""
        if e.get("image"):
            img_path = f"images/{e['image']}"
            gen_img = f"[![{num}]({img_path})]({img_path})"
        block = []
        summary = f"# {num}" if not title else f"# {num} — {title}"
        block.append(f"<details><summary>{summary}</summary>")
        if seed_img:
            block.append(seed_img)
        if gen_img:
            block.append(gen_img)
        if prompt_link:
            block.append(f"Prompt: {prompt_link}")
        block.append("</details>")
        blocks.append("\n".join(block))
    return "\n\n".join(blocks)

def first_three_words(text):
    s = (text or "").strip()
    if not s:
        return ""
    tokens = [t.strip(" ,.;:—-\"'()[]") for t in s.split()]
    tokens = [t for t in tokens if t and any(c.isalpha() for c in t)]
    return " ".join(tokens[:3])

def derive_title(text):
    s = (text or "").strip()
    if not s:
        return ""
    first = s.split(",", 1)[0].strip()
    if not first:
        words = s.split()
        first = " ".join(words[:6]).strip()
    if len(first) > 80:
        first = first[:80].rstrip(" ,.;-")
    return first

def write_readme():
    entries = collect_entries()
    md = build_readme(entries)
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(md)

def snapshot():
    return set(os.listdir(images_dir)), set(os.listdir(prompts_dir))

def watch(interval=2):
    ensure_dirs()
    a, b = snapshot()
    write_readme()
    while True:
        time.sleep(interval)
        a2, b2 = snapshot()
        if a2 != a or b2 != b:
            write_readme()
            a, b = a2, b2

def main():
    if "--watch" in sys.argv:
        watch()
    else:
        write_readme()

if __name__ == "__main__":
    main()
