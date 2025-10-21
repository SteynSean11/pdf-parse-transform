# validate.ps1 - PowerShell version of the validation script for Windows

# Exit immediately if a command exits with a non-zero status
$ErrorActionPreference = "Stop"

# --- Helper Functions ---

function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
    exit 1
}

# --- Validation Checks ---

Write-Info "Starting project validation..."

# 1. Check if Poetry is installed
try {
    $poetryVersion = & poetry --version 2>$null
    Write-Info "Poetry found: $poetryVersion"
} catch {
    Write-Error "Poetry is not installed. Please install Poetry to continue."
}

# 2. Check for essential files
Write-Info "Checking for essential configuration files..."
$essentialFiles = @("pyproject.toml", "poetry.lock", "Dockerfile", "docker-compose.yml")
foreach ($file in $essentialFiles) {
    if (!(Test-Path $file)) {
        Write-Error "Essential file not found: $file"
    }
    Write-Host " - Found $file"
}

# 3. Check if pyproject.toml and poetry.lock are in sync
Write-Info "Verifying consistency between pyproject.toml and poetry.lock..."
try {
    & poetry check --lock
    Write-Success "poetry.lock is consistent with pyproject.toml"
} catch {
    Write-Error "poetry.lock is not consistent with pyproject.toml. Please run 'poetry lock' to update."
}

# --- All Checks Passed ---

Write-Success "Project validation complete. All checks passed."

# --- Execute Command ---

# If arguments are passed to the script, execute them
if ($args.Count -gt 0) {
    $command = $args -join " "
    Write-Info "Executing command: $command"
    Invoke-Expression $command
}
