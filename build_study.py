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
    "robotica": ("Robotica", "Siciliano, Villani, Oriolo, De Luca - Foundations of Robotics"),
    "ml": ("Machine Learning", "Bishop - Pattern Recognition and Machine Learning"),
    "elettronica": ("Elettronica", "Embedded Systems"),
    "ros": ("ROS", "Programming Robots with ROS"),
    "shell": ("Linux e shell", "The Linux Command Line"),
    "consensus": ("Sistemi Multi-Agente", "Sanai Dashti, Seatzu, Franceschelli - Dynamic Consensus on the Median Value in Open Multi-Agent Systems (IEEE CDC 2019)"),
    "aerial_manip": ("Manipolazione Aerea", "Eskandarpour, Soltanshah, Gupta, Mehrandezh - Decoupled Dynamic Modeling and Tube-Based LPV-MPC for Aerial Manipulation (IEEE TAES 2025)"),
    "amr": ("Robotica Autonoma e Mobile", "Oriolo - Autonomous and Mobile Robotics (corso DIAG, Sapienza) + Siciliano et al., Foundations of Robotics"),
    "amr_en": ("Autonomous and Mobile Robotics", "Oriolo - Autonomous and Mobile Robotics (DIAG, Sapienza course) + Siciliano et al., Foundations of Robotics"),
    "controlli_es": ("Controlli Automatici - Esercizi", "Lanari, Oriolo - Controlli Automatici: Esercizi di Sintesi"),
    "controlli_es_en": ("Automatic Control - Exercises", "Lanari, Oriolo - Controlli Automatici: Esercizi di Sintesi"),
}


# titoli dei capitoli del libro: senza questi la lista mostrerebbe il titolo
# del primo modulo, che copre solo una parte del capitolo
CHAPTERS = {
    "controlli": {
        1: "Panoramica e storia della retroazione",
        2: "Modelli dinamici",
        3: "Risposta dinamica",
        4: "Prima analisi della retroazione",
        5: "Il metodo del luogo delle radici",
        6: "Progetto in frequenza",
        7: "Progetto nello spazio di stato",
        8: "Controllo digitale",
        9: "Sistemi non lineari",
    },
    "robotica": {
        1: "Introduzione",
        2: "Cinematica",
        3: "Cinematica differenziale e statica",
        4: "Pianificazione di traiettoria",
        5: "Dinamica",
        6: "Controllo del moto",
        7: "Robot mobili su ruote",
        8: "Controllo visivo",
        9: "Pianificazione del moto",
        10: "Controllo di forza",
        11: "Manipolatori con giunti elastici",
    },
    "consensus": {
        1: "Consenso dinamico sulla mediana",
    },
    "aerial_manip": {
        1: "Modellazione disaccoppiata e controllo LPV-MPC",
    },
    "amr": {
        1: "Introduzione: applicazioni, problemi, architetture",
        2: "Spazio delle configurazioni",
        3: "Robot mobili su ruote 1: meccanica",
        4: "Robot mobili su ruote 2: modelli cinematici",
        5: "Robot mobili su ruote 3: pianificazione di percorso/traiettoria",
        6: "Robot mobili su ruote 4: inseguimento di traiettoria",
        7: "Robot mobili su ruote 5: regolazione",
        8: "Robot mobili su ruote 6: mobile manipulator",
        9: "Percezione: sensori per robot mobili",
        10: "Localizzazione 1: localizzazione odometrica",
        11: "Localizzazione 2: filtro di Kalman",
        12: "Localizzazione 3: landmark-based e SLAM",
        13: "Pianificazione del moto 1: retrazione e cell decomposition",
        14: "Pianificazione del moto 2: pianificazione probabilistica",
        15: "Pianificazione del moto 3: campi potenziali artificiali",
        16: "Robot umanoidi 1: introduzione",
        17: "Robot umanoidi 2: architetture e whole-body control",
        18: "Robot umanoidi 3: generazione dell'andatura",
        19: "Locomozione umanoide: una dimostrazione",
        20: "Casi di studio ed esame",
    },
    "controlli_es": {
        1: "Analisi dei sistemi a retroazione",
        2: "Sintesi nel dominio della frequenza",
        3: "Sintesi con il luogo delle radici",
        4: "Sintesi nel dominio del tempo",
    },
}

CHAPTERS["amr_en"] = {
    1: "Introduction: applications, problems, architectures",
    2: "Configuration space",
    3: "Wheeled mobile robots 1: mechanics",
    4: "Wheeled mobile robots 2: kinematic models",
    5: "Wheeled mobile robots 3: path/trajectory planning",
    6: "Wheeled mobile robots 4: trajectory tracking",
    7: "Wheeled mobile robots 5: regulation",
    8: "Wheeled mobile robots 6: mobile manipulators",
    9: "Perception: sensors for mobile robots",
    10: "Localization 1: odometric localization",
    11: "Localization 2: Kalman filter",
    12: "Localization 3: landmark-based and SLAM",
    13: "Motion planning 1: retraction and cell decomposition",
    14: "Motion planning 2: probabilistic planning",
    15: "Motion planning 3: artificial potential fields",
    16: "Humanoid robots 1: introduction",
    17: "Humanoid robots 2: architectures and whole-body control",
    18: "Humanoid robots 3: gait generation",
    19: "Humanoid locomotion: a demonstration",
    20: "Case studies and exam problems",
}
CHAPTERS["controlli_es_en"] = {
    1: "Feedback system analysis",
    2: "Frequency-domain synthesis",
    3: "Root-locus synthesis",
    4: "Time-domain synthesis",
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
            titles = CHAPTERS.get(slug, {})
            chapters = [{"n": c, "title": titles.get(c, f"Capitolo {c}")}
                        for c in sorted({mod["chapter"] for mod in modules})]
            subjects.append({"slug": slug, "label": label, "book": book,
                             "chapters": chapters, "modules": modules})
    OUT.write_text(json.dumps({"subjects": subjects}, ensure_ascii=False, indent=1),
                   encoding="utf-8")
    total = sum(len(s["modules"]) for s in subjects)
    for s in subjects:
        chapters = sorted({mod["chapter"] for mod in s["modules"]})
        print(f"{s['label']}: {len(s['modules'])} moduli, capitoli {chapters}")
    print(f"{total} moduli -> {OUT}")


if __name__ == "__main__":
    main()
