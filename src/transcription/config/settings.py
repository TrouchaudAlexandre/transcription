from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional


try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional dependency
    load_dotenv = None


@dataclass(frozen=True)
class Settings:
    playlist_csv: str
    files_list_csv: str
    log_path: str
    audio_base_path: str
    video_base_path: str
    segmentation_root: str
    transcription_root: str
    output_root: str
    segment_length_seconds: int
    whisper_model: str
    language: str
    use_mock: bool


def load_settings() -> Settings:
    if load_dotenv is not None:
        load_dotenv()

    def env(name: str, default: str) -> str:
        return os.getenv(name, default)

    return Settings(
        playlist_csv=env(
            "PLAYLIST_CSV",
            "/content/drive/MyDrive/Colab Notebooks/ressource/playlists.csv",
        ),
        files_list_csv=env(
            "FILES_LIST_CSV",
            "/content/drive/MyDrive/Colab Notebooks/ressource/files_list.csv",
        ),
        log_path=env(
            "LOG_PATH",
            "/content/drive/MyDrive/Colab Notebooks/ressource/log.txt",
        ),
        audio_base_path=env(
            "AUDIO_BASE_PATH",
            "/content/drive/MyDrive/Colab Notebooks/ressource/audio",
        ),
        video_base_path=env(
            "VIDEO_BASE_PATH",
            "/content/drive/MyDrive/Colab Notebooks/ressource/video",
        ),
        segmentation_root=env(
            "SEGMENTATION_ROOT",
            "/content/drive/MyDrive/Colab Notebooks/ressource/segmentation",
        ),
        transcription_root=env(
            "TRANSCRIPTION_ROOT",
            "/content/drive/MyDrive/Colab Notebooks/creation/transcription",
        ),
        output_root=env(
            "OUTPUT_ROOT",
            "/content/drive/MyDrive/Colab Notebooks/creation/resultat",
        ),
        segment_length_seconds=int(env("SEGMENT_LENGTH_SECONDS", "60")),
        whisper_model=env("WHISPER_MODEL", "large-v3-turbo"),
        language=env("WHISPER_LANGUAGE", "Arabic"),
        use_mock=env("USE_MOCK", "false").lower() == "true",
    )


def override_settings(settings: Settings, **kwargs: Optional[str]) -> Settings:
    data = settings.__dict__.copy()
    for key, value in kwargs.items():
        if value is None:
            continue
        if key == "segment_length_seconds":
            data[key] = int(value)
        elif key == "use_mock":
            data[key] = str(value).lower() == "true"
        else:
            data[key] = value
    return Settings(**data)
