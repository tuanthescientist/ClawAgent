.PHONY: help install dev test lint format clean docker-build docker-run docker-stop

help:
	@echo "ClawAgent development commands"
	@echo "============================="
	@echo "make install      Install Python dependencies"
	@echo "make dev          Run the FastAPI development server"
	@echo "make test         Run the test suite"
	@echo "make lint         Run static checks"
	@echo "make format       Format the codebase with black"
	@echo "make clean        Remove caches and build artifacts"
	@echo "make docker-build Build the Docker image"
	@echo "make docker-run   Start the Docker services"
	@echo "make docker-stop  Stop the Docker services"

install:
	pip install -r requirements.txt

dev:
	uvicorn src.main:app --reload

test:
	py -m pytest -v

lint:
	flake8 src tests
	mypy src --ignore-missing-imports

format:
	black src tests

clean:
	py -c "import pathlib, shutil; [shutil.rmtree(p, ignore_errors=True) for p in pathlib.Path('.').rglob('__pycache__')]"
	py -c "import pathlib; [p.unlink() for p in pathlib.Path('.').rglob('*.pyc')]"

docker-build:
	docker build -t clawagent:latest .

docker-run:
	docker-compose up --build

docker-stop:
	docker-compose down
