@echo off
IF "%1"=="run" (
    poetry run uvicorn application.main:app --reload
) ELSE IF "%1"=="db-init" (
    poetry run python infrastructure/helpers/database/init_db.py
) ELSE IF "%1"=="test" (
    poetry run pytest tests/
) ELSE (
    echo Comando no reconocido: %1
)
