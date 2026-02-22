# Runner Colab (2 cellules)

## Cellule 1 - Setup et clone
```bash
from google.colab import drive
drive.mount('/content/drive')

REPO_URL = "https://github.com/<org-or-user>/<repo>.git"
BRANCH = "main"
PROJECT_DIR = "/content/transcription"

!rm -rf "$PROJECT_DIR"
!git clone --depth 1 --branch "$BRANCH" "$REPO_URL" "$PROJECT_DIR"
!python -m pip install --upgrade pip
!python -m pip install python-dotenv pytube openai-whisper
!apt-get update -y && apt-get install -y ffmpeg
```

## Cellule 2 - Config et execution pipeline
```bash
import os

PROJECT_DIR = "/content/transcription"
os.chdir(PROJECT_DIR)

# 1) Copier l'exemple de config puis adapter les chemins si besoin
!cp -f .env.example .env

# 2) Lancer les etapes V1
!PYTHONPATH=src python -m transcription.cli.main --step download
!PYTHONPATH=src python -m transcription.cli.main --step segment
!PYTHONPATH=src python -m transcription.cli.main --step transcribe
!PYTHONPATH=src python -m transcription.cli.main --step merge
```

## Notes
- Modifier `REPO_URL` avant execution.
- Modifier `.env` apres copie si tes chemins Drive differents.
- Tu peux relancer une etape seule (`--step segment` par ex.) grace au CSV d'etat.
