#!/bin/bash

# NetDiag Remote Runner

# --- Configuration ---
REPO_OWNER="zootsman"
REPO_NAME="netdiag"
BRANCH="master"
TARBALL_URL="https://github.com/${REPO_OWNER}/${REPO_NAME}/archive/refs/heads/${BRANCH}.tar.gz"

# --- Helper Functions ---
print_info() {
    echo -e "\033[34m[INFO]\033[0m $1"
}

print_error() {
    echo -e "\033[31m[ERROR]\033[0m $1" >&2
    exit 1
}

cleanup() {
    print_info "Cleaning up temporary files..."
    rm -rf "$TMP_DIR"
}

# --- Main Execution ---
print_info "Starting NetDiag remote execution..."

# 1. Create a temporary directory
TMP_DIR=$(mktemp -d)
trap cleanup EXIT
print_info "Created temporary directory at $TMP_DIR"
cd "$TMP_DIR" || exit 1

# 2. Check for dependencies
print_info "Checking for required commands: curl, tar, python..."
command -v curl >/dev/null 2>&1 || print_error "curl is not installed. Please install it first."
command -v tar >/dev/null 2>&1 || print_error "tar is not installed. Please install it first."
command -v python >/dev/null 2>&1 || print_error "python is not installed. Please install it first."

# 3. Download and extract the repository
print_info "Downloading repository from GitHub..."
curl -sSL "$TARBALL_URL" -o repo.tar.gz || print_error "Failed to download repository."
tar -xzf repo.tar.gz --strip-components=1 || print_error "Failed to extract repository."

# 4. Install Python dependencies in a temporary venv
print_info "Creating temporary virtual environment and installing dependencies..."
python -m venv .venv || print_error "Failed to create virtual environment."
source .venv/bin/activate || print_error "Failed to activate virtual environment."
pip install -r requirements.txt || print_error "Failed to install Python dependencies."

# 5. Run the main script
print_info "Running NetDiag..."
echo "----------------------------------------"
python netdiag.py
echo "----------------------------------------"

print_info "NetDiag execution finished."
# The 'trap' will handle cleanup on exit.
exit 0
