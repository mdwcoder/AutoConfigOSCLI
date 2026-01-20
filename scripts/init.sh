#!/bin/bash
set -e

REPO_URL="https://github.com/mdwcoder/AutoConfigOSCLI"
INSTALL_DIR="$HOME/.autoconfigoscli"
REPO_DIR="$INSTALL_DIR/repo"
VENV_DIR="$INSTALL_DIR/venv"
DATA_DIR="$INSTALL_DIR/data"
BIN_DIR="$HOME/bin" 
# Use ~/bin or ~/.local/bin depending on preference, but user requested symlink. 
# We'll use /usr/local/bin if possible, or advise adding ~/bin to PATH.
# Actually, the user asked for "Crea symlink del comando `autoconfigoscli`". 
# Common practice is /usr/local/bin (needs sudo) or ~/.local/bin. 
# We'll try ~/.local/bin first as it's cleaner.

echo ">>> AutoConfigOSCLI Installer"

# 1. Prepare Directories
mkdir -p "$DATA_DIR" "$INSTALL_DIR/logs" "$INSTALL_DIR/backups"
echo "Created directories in $INSTALL_DIR"

# 2. Clone/Update Repo (Simulated logic since we are already in the repo for this exercise, 
# but usually this script pulls from git. We will assume the script is run FROM the repo or curls it.)
# For the sake of this constrained env, we will assume we are "installing" the current directory to ~/.autoconfigoscli/repo
# logic if we were truly remote:
# if [ -d "$REPO_DIR" ]; then
#     cd "$REPO_DIR" && git pull
# else
#     git clone "$REPO_URL" "$REPO_DIR"
# fi

# Since we are creating the project now, let's copy the current source to the target dir to simulate "Installation"
echo "Installing to $REPO_DIR..."
rm -rf "$REPO_DIR"
mkdir -p "$REPO_DIR"
cp -r . "$REPO_DIR"

# 3. Create Venv
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

# 4. Install Dependencies
echo "Installing dependencies..."
"$VENV_DIR/bin/pip" install -r "$REPO_DIR/requirements.txt" --upgrade --quiet

# 5. Create Wrapper/Symlink
WRAPPER="$INSTALL_DIR/autoconfigoscli"
cat <<EOF > "$WRAPPER"
#!/bin/bash
source "$VENV_DIR/bin/activate"
export PYTHONPATH="$REPO_DIR"
python3 -m autoconfigoscli.cli "\$@"
EOF
chmod +x "$WRAPPER"

# Symlink to path
# Try to put in ~/.local/bin if exists, else suggest
TARGET_BIN="$HOME/.local/bin"
mkdir -p "$TARGET_BIN"
ln -sf "$WRAPPER" "$TARGET_BIN/autoconfigoscli"

echo ">>> Installation Complete!"
echo "Ensure $TARGET_BIN is in your PATH."
echo "Run 'autoconfigoscli --help' to get started."
