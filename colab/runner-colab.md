# Runner Colab (2 cellules)

## Cellule 1 - Setup et clone
```bash
from google.colab import drive
import os
import shutil
import subprocess

drive.mount('/content/drive')

REPO_URL = "https://github.com/<org-or-user>/<repo>.git"
BRANCH = "main"
PROJECT_DIR = "/content/transcription"

# Evite les erreurs getcwd si la session etait deja dans PROJECT_DIR
os.chdir("/content")
if os.path.exists(PROJECT_DIR):
    shutil.rmtree(PROJECT_DIR)

subprocess.run(
    ["git", "clone", "--depth", "1", "--branch", BRANCH, REPO_URL, PROJECT_DIR],
    check=True,
)
subprocess.run(["python", "-m", "pip", "install", "--upgrade", "pip"], check=True)
subprocess.run(
    ["python", "-m", "pip", "install", "python-dotenv", "pytube", "openai-whisper"],
    check=True,
)
subprocess.run(["apt-get", "update", "-y"], check=True)
subprocess.run(["apt-get", "install", "-y", "ffmpeg"], check=True)
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
