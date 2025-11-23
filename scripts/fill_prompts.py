import os
import sys
import subprocess
import re
import time

root = os.getcwd()
prompts_dir = os.path.join(root, "prompts")

def is_empty(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return not f.read().strip()
    except Exception:
        return True

def list_empty_txts():
    items = []
    for f in sorted(os.listdir(prompts_dir)):
        if len(f) == 8 and f.endswith(".txt") and f[:4].isdigit():
            p = os.path.join(prompts_dir, f)
            if is_empty(p):
                items.append((f[:4], p))
    return items

def read_source(mode, src_file):
    if mode == "stdin":
        try:
            return sys.stdin.read()
        except Exception:
            return ""
    if mode == "clipboard":
        try:
            return subprocess.check_output(["pbpaste"], text=True)
        except Exception:
            return ""
    if mode == "file" and src_file:
        try:
            with open(src_file, "r", encoding="utf-8") as f:
                return f.read()
        except Exception:
            return ""
    lines = []
    while True:
        try:
            line = sys.stdin.readline()
        except Exception:
            break
        if not line:
            break
        if line.strip() == "END":
            break
        lines.append(line)
    return "\n".join(lines)

def fill_one(num, path, mode="interactive", src_file=None):
    print(f"Paste prompt for {num}. Finish with END or Ctrl+D.")
    text = read_source(mode, src_file).strip()
    if not text:
        print("Skipped (empty input)")
        return False
    with open(path, "w", encoding="utf-8") as f:
        f.write(text + "\n")
    print(f"Wrote {os.path.relpath(path, root)}")
    return True

def build_readme():
    try:
        subprocess.run([sys.executable, os.path.join(root, "scripts", "build_readme.py")], check=False)
    except Exception:
        pass

def main():
    os.makedirs(prompts_dir, exist_ok=True)
    targets = []
    mode = "interactive"
    src_file = None
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if re.fullmatch(r"\d{4}", arg):
            p = os.path.join(prompts_dir, f"{arg}.txt")
            if os.path.exists(p) and is_empty(p):
                targets = [(arg, p)]
            else:
                print("No empty txt for", arg)
        elif re.fullmatch(r"\d{4}-\d{4}", arg):
            a, b = arg.split("-")
            rng = range(int(a), int(b) + 1)
            for n in rng:
                s = f"{n:04d}"
                p = os.path.join(prompts_dir, f"{s}.txt")
                if os.path.exists(p) and is_empty(p):
                    targets.append((s, p))
        else:
            targets = list_empty_txts()
        if "--stdin" in sys.argv:
            mode = "stdin"
        elif "--clipboard" in sys.argv:
            mode = "clipboard"
        elif "--clipboard-per-entry" in sys.argv or "--clipstep" in sys.argv:
            mode = "clipstep"
        elif "--clipboard-watch" in sys.argv or "--watchclip" in sys.argv:
            mode = "clipwatch"
        elif "--editor" in sys.argv:
            mode = "editor"
        elif "--from-file" in sys.argv:
            i = sys.argv.index("--from-file")
            if i + 1 < len(sys.argv):
                src_file = sys.argv[i + 1]
                mode = "file"
    else:
        targets = list_empty_txts()
    if not targets:
        print("No empty prompt txt files found.")
        return
    if mode == "stdin" and len(targets) != 1:
        print("stdin mode requires a single number (e.g. 0002)")
        return
    last_clip = None
    for num, path in targets:
        print(f"---- {num} ----")
        if mode == "clipstep":
            try:
                inp = input("Press Enter to capture clipboard, 's' to skip, 'q' to quit: ").strip().lower()
            except EOFError:
                inp = ""
            if inp == "q":
                break
            if inp == "s":
                continue
            text = read_source("clipboard", None).strip()
            if not text:
                print("Skipped (clipboard empty)")
            else:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(text + "\n")
                print(f"Wrote {os.path.relpath(path, root)}")
        elif mode == "clipwatch":
            print("Waiting for clipboard… copy your prompt now")
            for _ in range(6000):
                text = read_source("clipboard", None).strip()
                if text and text != (last_clip or ""):
                    with open(path, "w", encoding="utf-8") as f:
                        f.write(text + "\n")
                    print(f"Wrote {os.path.relpath(path, root)}")
                    last_clip = text
                    break
                time.sleep(0.2)
            else:
                print("Skipped (clipboard did not change)")
        elif mode == "editor":
            try:
                subprocess.run(["open", "-a", "TextEdit", path], check=False)
            except Exception:
                subprocess.run(["open", path], check=False)
            try:
                input("TextEdit opened. Paste and save, then press Enter to continue… ")
            except EOFError:
                pass
            if is_empty(path):
                print("Skipped (file still empty)")
            else:
                print(f"Saved {os.path.relpath(path, root)}")
        else:
            fill_one(num, path, mode=mode, src_file=src_file)
        print("")
    build_readme()

if __name__ == "__main__":
    main()
