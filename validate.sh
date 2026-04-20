#!/bin/bash

# All in script for linting, type checking, and testing. This is what CI runs.

set -e

echo "=== Running full validation pipeline ==="
hatch run validate

echo ""
echo "=== All validations passed! ==="
