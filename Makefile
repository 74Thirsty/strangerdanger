.PHONY: backend-install backend-run test seed

backend-install:
	pip install -r backend/requirements.txt

backend-run:
	uvicorn backend.app.main:app --reload

test:
	pytest -q

seed:
	python scripts/seed_demo.py
