# CLAUDE.md

## Project Overview

This is a **LinkedIn Learning exercise repository** for the German-language course **"Python für Nicht-Programmierer:innen"** (Python for Non-Programmers) by Dr. Julia Imlauer. It teaches fundamental Python programming through hands-on exercises, progressing from basic variables to building interactive games.

**Language**: German (code comments, variable names, and documentation are in German)
**Runtime**: Python 3.x (standard library only, no external dependencies)

## Repository Structure

```
├── loesungen/                  # Solution files organized by course module
│   ├── modul_2/                # Variables, data types, lists
│   ├── modul_3/                # Control flow (conditionals, loops)
│   ├── modul_4/                # Functions
│   ├── modul_5/                # Rock-Paper-Scissors game
│   └── modul_6/                # Tic-Tac-Toe game
├── video_erklaerungen/         # Reference code for video tutorials
├── uebungs_datei.py            # Exercise starter template
├── .devcontainer/              # GitHub Codespaces configuration
├── .vscode/                    # VS Code editor settings
├── .github/                    # GitHub templates and workflows
├── requirements.txt            # Empty (no external dependencies)
├── README.md                   # Course description and instructions
├── CONTRIBUTING.md             # Contribution policy (PRs not accepted)
├── LICENSE                     # LinkedIn Learning proprietary license
└── NOTICE                      # Copyright notice
```

## Key Conventions

- **All code is beginner-level Python** using only built-in functions and the `random` module
- **German naming**: Variables, functions, and comments use German (e.g., `ausgabe_feld`, `gewinn_abfrage`, `spieler`)
- **No external packages**: `requirements.txt` is intentionally empty; all code uses Python standard library
- **Module progression**: Modules 2-6 build incrementally from basic types to complete game implementations
- **Tab size**: 2 spaces (configured in `.vscode/settings.json`)

## Development Environment

- **Primary environment**: GitHub Codespaces (configured via `.devcontainer/devcontainer.json`)
- **Editor**: VS Code with Python extension (`ms-python.python`)
- **Theme**: Visual Studio Dark
- **Auto-setup**: `pip install -r requirements.txt` runs on container creation

## Running Code

All files are standalone Python scripts. Run any file directly:

```bash
python loesungen/modul_2/02_02_lsg.py
python loesungen/modul_5/05_03_lsg.py    # Interactive Rock-Paper-Scissors
python loesungen/modul_6/06_04_lsg.py    # Interactive Tic-Tac-Toe
```

Some scripts (modules 5 and 6) require interactive terminal input.

## Testing and CI

- **No test framework** is configured (educational project, not a library)
- **No linters or formatters** are configured
- **CI/CD**: Only a manual `workflow_dispatch` workflow (`Copy To Branches`) for LinkedIn Learning platform integration

## Important Policies

- **Pull requests are not accepted** (stated in `CONTRIBUTING.md` and PR template)
- **License**: LinkedIn Learning Exercise File License (proprietary, non-redistributable)
- **Code owners**: Not specified (`.github/CODEOWNERS` is empty)

## File Naming Convention

- Solution files: `XX_YY_lsg.py` where `XX` = module number, `YY` = exercise number, `lsg` = "Lösung" (solution)
- Video explanations: `modul_X_erklaerungen.py`
