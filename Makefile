.PHONY: help setup install test lint clean run docker-build docker-run docker-stop

help:
	@echo "Available commands:"
	@echo "  setup        - Set up development environment"
	@echo "  install     - Install dependencies"
	@echo "  test        - Run tests"
	@echo "  lint        - Run code linting"
	@echo "  clean       - Clean up generated files"
	@echo "  run         - Run the application locally"
	@echo "  docker-build - Build Docker containers"
	@echo "  docker-run   - Run Docker containers"
	@echo "  docker-stop  - Stop Docker containers"

setup: install
	cp .env.example .env
	mkdir -p uploads
	mkdir -p logs

install:
	python -m pip install --upgrade pip
	pip install -r requirements.txt

test:
	pytest --cov=app --cov-report=term-missing

lint:
	flake8 app tests
	black app tests --check

clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -r {} +
	find . -type d -name "*.egg" -exec rm -r {} +
	find . -type d -name ".pytest_cache" -exec rm -r {} +
	find . -type d -name ".coverage" -exec rm -r {} +
	rm -rf build/
	rm -rf dist/
	rm -rf .eggs/
	rm -rf uploads/*
	rm -rf logs/*

run:
	flask run --debug

docker-build:
	docker-compose build

docker-run:
	docker-compose up

docker-stop:
	docker-compose down 