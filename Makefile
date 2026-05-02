run:
	uvicorn app.main:app --reload

migrate:
	alembic upgrade head

test:
	pytest

build-css:
	npm run build:css
