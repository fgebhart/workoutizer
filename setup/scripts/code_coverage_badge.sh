#!/bin/bash

# install tool to create coverage badge from data created by pytest-cov located in .coverage folger
pip install coverage-badge

echo "Note: Run tests with coverage to update coverage data: pytest wkz/tests -n4 --cov=wkz"

# create badge and save it to .github folder
coverage-badge -o .github/badges/coverage.svg -f