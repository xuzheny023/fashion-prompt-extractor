# -*- coding: utf-8 -*-
import sys, os, unicodedata

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TEXT_EXTS = {".py", ".json", ".md", ".yml", ".yaml", ".toml", ".cfg", ".ini", ".txt"}
ZERO_WIDTH = ["\u200b", "\u200c", "\u200d", "\ufeff", "\u200e", "\u200f"]

def read_text(path):
    with open(path, "rb") as f:
        raw = f.read()
    for enc in ("utf-8", "gbk"):
        try:
            return raw.decode(enc)
        except Exception:
            continue
    return raw.decode("utf-8", errors="replace")

def write_text(path, text):
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    with open(path, "wb") as f:
        f.write(text.encode("utf-8"))

def normalize_text(text, is_py=False):
    norm = unicodedata.normalize("NFKC", text)
    for z in ZERO_WIDTH:
        norm = norm.replace(z, "")
    if is_py and not norm.startswith("# -*- coding: utf-8 -*-"):
        lines = norm.split("\n")
        if lines and not lines[0].startswith("#!"):
            lines.insert(0, "# -*- coding: utf-8 -*-")
        norm = "\n".join(lines)
    return norm

def process_file(path):
    text = read_text(path)
    new_text = normalize_text(text, path.endswith(".py"))
    if new_text != text:
        write_text(path, new_text)
        print(f"[fixed] {os.path.relpath(path, ROOT)}")

def main():
    for root, _, files in os.walk(ROOT):
        if any(x in root for x in [".venv", "__pycache__", ".git"]):
            continue
        for name in files:
            ext = os.path.splitext(name)[1].lower()
            if ext in TEXT_EXTS:
                process_file(os.path.join(root, name))

if __name__ == "__main__":
    main()


