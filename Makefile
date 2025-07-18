run:
	poetry run python application/main.py

db-init:
	poetry run python infrastructure/helpers/database/init_db.py

test:
	poetry run pytest tests/
