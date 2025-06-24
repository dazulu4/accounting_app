run:
	poetry run uvicorn application.main:app --reload

db-init:
	poetry run python infrastructure/helpers/database/init_db.py

test:
	poetry run pytest tests/
