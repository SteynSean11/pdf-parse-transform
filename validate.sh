#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Helper Functions ---

# Function to print a formatted message
info() {
    echo -e "\033[34m[INFO]\033[0m $1"
}

# Function to print a success message
success() {
    echo -e "\033[32m[SUCCESS]\033[0m $1"
}

# Function to print an error message and exit
error() {
    echo -e "\033[31m[ERROR]\033[0m $1" >&2
    exit 1
}

# --- Validation Checks ---

info "Starting project validation..."

# 1. Check if Poetry is installed
if ! command -v poetry &> /dev/null; then
    error "Poetry is not installed. Please install Poetry to continue."
fi

# 2. Check for essential files
info "Checking for essential configuration files..."
ESSENTIAL_FILES=("pyproject.toml" "poetry.lock" "Dockerfile" "docker-compose.yml")
for file in "${ESSENTIAL_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        error "Essential file not found: $file"
    fi
    echo " - Found $file"
done

# 3. Check if pyproject.toml and poetry.lock are in sync
info "Verifying consistency between pyproject.toml and poetry.lock..."
if ! poetry check --lock; then
    error "poetry.lock is not consistent with pyproject.toml. Please run 'poetry lock' to update."
fi

# --- All Checks Passed ---

success "Project validation complete. All checks passed."

# --- Execute Command ---

# If arguments are passed to the script, execute them
if [ "$#" -gt 0 ]; then
    info "Executing command: $@"
    exec "$@"
fi
