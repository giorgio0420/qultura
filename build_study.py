"""Raccoglie i moduli di studio in study.json, il file che la PWA legge.

I .md restano locali (study/ e' in .gitignore): solo il JSON viene pubblicato.

    python build_study.py
"""

import json
import pathlib
import re

SRC = pathlib.Path("study")
OUT = pathlib.Path("study.json")

# materia -> (etichetta mostrata, libro di riferimento)
SUBJECTS = {
    "controlli": ("Controlli Automatici", "Franklin, Feedback Control of Dynamic Systems"),
    "robotica": ("Robotica", "Siciliano, Villani, Oriolo - Foundations of Robotics"),
    "ml": ("Machine Learning", "Bishop - Pattern Recognition and Machine Learning"),
    "elettronica": ("Elettronica", "Embedded Systems"),
    "ros": ("ROS", "Programming Robots with ROS"),
    "shell": ("Linux e shell", "The Linux Command Line"),
}


def parse(path):
    """Estrae numero, titolo e corpo da un file modulo-X.Y.md."""
    text = path.read_text(encoding="utf-8")
    m = re.search(r"^###\s*Modulo\s*([\d.]+)\s*:\s*(.+)$", text, re.M)
    if not m:
        return None
    number, title = m.group(1), m.group(2).strip()
    chapter = int(number.split(".")[0])
    # il corpo comincia dopo la riga del titolo; il separatore finale non serve
    body = text[m.end():].strip().removesuffix("---").strip()
    return {"number": number, "chapter": chapter, "title": title, "body": body}


def main():
    subjects = []
    for slug, (label, book) in SUBJECTS.items():
        folder = SRC / slug
        if not folder.is_dir():
            continue
        modules = sorted(
            (mod for mod in (parse(p) for p in folder.glob("modulo-*.md")) if mod),
            key=lambda mod: [int(x) for x in mod["number"].split(".")],
        )
        if modules:
            subjects.append({"slug": slug, "label": label, "book": book,
                             "modules": modules})
    OUT.write_text(json.dumps({"subjects": subjects}, ensure_ascii=False, indent=1),
                   encoding="utf-8")
    total = sum(len(s["modules"]) for s in subjects)
    for s in subjects:
        chapters = sorted({mod["chapter"] for mod in s["modules"]})
        print(f"{s['label']}: {len(s['modules'])} moduli, capitoli {chapters}")
    print(f"{total} moduli -> {OUT}")


if __name__ == "__main__":
    main()
