# THRESHOLD_ONSET — Common tasks
# Use: make <target>

.PHONY: install run check health config test test-api docker-build docker-run help

install:
	pip install -e .

run:
	threshold-onset run

check:
	threshold-onset check "$(if $(TEXT),$(TEXT),Action before knowledge)"

health:
	threshold-onset health

config:
	threshold-onset config

test:
	python -m pytest tests/ threshold_onset/semantic/tests/ -v --tb=short

test-api:
	python -m pytest tests/test_api.py -v --tb=short

test-cov:
	pip install pytest-cov
	python -m pytest tests/test_api.py --cov=threshold_onset --cov-report=term-missing -q

docker-build:
	docker build -t threshold-onset:latest .

docker-run:
	docker run --rm threshold-onset:latest

docker-compose:
	docker compose up

health-server:
	python scripts/health_server.py

help:
	@echo "THRESHOLD_ONSET targets:"
	@echo "  install       - pip install -e ."
	@echo "  run           - threshold-onset run"
	@echo "  check         - Quick check (TEXT='...' for custom input)"
	@echo "  health        - threshold-onset health"
	@echo "  config        - Show config"
	@echo "  test          - Run all tests"
	@echo "  test-api      - Run API integration tests"
	@echo "  test-cov      - Run tests with coverage"
	@echo "  docker-build  - Build Docker image"
	@echo "  docker-run    - Run Docker container"
	@echo "  docker-compose- docker compose up"
	@echo "  health-server - Start HTTP health/process server"
