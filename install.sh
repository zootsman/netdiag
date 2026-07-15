#!/bin/bash

# NetDiag Installer

# --- Configuration ---
REPO_URL="https://github.com/zootsman/netdiag.git"
INSTALL_DIR="$HOME/netdiag"

# --- Helper Functions ---
print_info() {
    echo -e "\033[34m[INFO]\033[0m $1"
}

print_success() {
    echo -e "\033[32m[SUCCESS]\033[0m $1"
}

print_error() {
    echo -e "\033[31m[ERROR]\033[0m $1" >&2
    exit 1
}

# --- Main Installation ---
print_info "Starting NetDiag installation..."

# 1. Check for dependencies
print_info "Checking for required commands: git, python..."
command -v git >/dev/null 2>&1 || print_error "git is not installed. Please install it first."
command -v python >/dev/null 2>&1 || print_error "python is not installed. Please install it first."

# 2. Clone the repository
if [ -d "$INSTALL_DIR" ]; then
    print_info "Directory $INSTALL_DIR already exists. Pulling latest changes..."
    cd "$INSTALL_DIR" || exit 1
    git pull origin master || print_error "Failed to pull latest changes."
else
    print_info "Cloning repository into $INSTALL_DIR..."
    git clone "$REPO_URL" "$INSTALL_DIR" || print_error "Failed to clone repository."
    cd "$INSTALL_DIR" || exit 1
fi

# 3. Install Python dependencies
print_info "Installing Python dependencies from requirements.txt..."
if [ -f "requirements.txt" ]; then
    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt || print_error "Failed to install Python dependencies."
else
    print_warning "requirements.txt not found. Skipping dependency installation."
fi

# 4. Final instructions
print_success "Installation complete!"
echo
echo "To run NetDiag, use the following commands:"
echo "1. Change to the installation directory:"
echo "   cd $INSTALL_DIR"
echo "2. Activate the virtual environment:"
echo "   source .venv/bin/activate"
echo "3. Run the script:"
echo "   python netdiag.py"
echo
