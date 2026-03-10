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
    [
        "python",
        "-m",
        "pip",
        "install",
        "python-dotenv",
        "yt-dlp",
        "openai-whisper",
        "openai",
        "google-genai",
    ],
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

# 1) Copier l'exemple de config
!cp -f .env.example .env

# 2) Adapter les parametres necessaires a la traduction
# Exemple:
# - TRANSLATION_API_KEY
# - TARGET_LANGUAGE
# - SOURCE_VARIANT
# - TRANSLATION_CONTEXT
# - TRANSLATION_MODEL=gpt-5-mini
# - TRANSLATION_PROVIDER=openai|gemini

# 3) Lancer les etapes du pipeline
!PYTHONPATH=src python -m transcription.cli.main --step download
!PYTHONPATH=src python -m transcription.cli.main --step segment
!PYTHONPATH=src python -m transcription.cli.main --step transcribe
!PYTHONPATH=src python -m transcription.cli.main --step translate
!PYTHONPATH=src python -m transcription.cli.main --step merge
```

## Notes
- Modifier `REPO_URL` avant execution.
- Modifier `.env` apres copie si tes chemins Drive ou tes parametres de traduction different.
- Pour la traduction, renseigner `TRANSLATION_API_KEY` dans `.env`.
- Si `TRANSLATION_PROVIDER=gemini`, `google-genai` est deja installe par ce runner.
- Pour un dialecte comme le tunisien, utiliser `SOURCE_VARIANT=tunisian_arabic` et completer `TRANSLATION_CONTEXT` si necessaire.
- Tu peux relancer une etape seule (`--step segment` par ex.) grace au CSV d'etat.
