#!/bin/bash


echo "=== mypy ==="
poetry run mypy --strict bookkeeper

echo "=== pylint ==="
poetry run pylint bookkeeper

echo "=== flake8 ==="
poetry run flake8 bookkeeper
