#!/bin/bash
set -e

echo "======================================"
echo "  AMP (Ascii Media Player) Installer"
echo "======================================"

# Detect OS
detect_os() {
    # Check for Termux (Android)
    if [ -d "/data/data/com.termux/files" ] || [ -n "$TERMUX_VERSION" ]; then
        echo "termux"
        return
    fi
    
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        case "$ID" in
            fedora|rhel|centos|rocky|alma)
                echo "rhel"
                ;;
            debian|ubuntu|linuxmint)
                echo "debian"
                ;;
            arch|manjaro|archlinux)
                echo "arch"
                ;;
            opensuse|sles)
                echo "suse"
                ;;
            *)
                echo "unknown"
                ;;
        esac
    elif [ -f /etc/redhat-release ]; then
        echo "rhel"
    elif [ -f /etc/debian_version ]; then
        echo "debian"
    else
        echo "unknown"
    fi
}

OS=$(detect_os)
echo "Detected OS: $OS"

# Install dependencies based on OS
install_deps() {
    echo ""
    echo "Installing dependencies..."

    case "$OS" in
        rhel)
            echo "Installing for RHEL-based distro..."
            sudo dnf install -y ffmpeg ffmpeg-devel cargo python3-devel gcc
            ;;
        debian)
            echo "Installing for Debian-based distro..."
            sudo apt-get update
            sudo apt-get install -y ffmpeg libavcodec-dev libavformat-dev libswscale-dev libavdevice-dev cargo python3 libncurses-dev
            ;;
        arch)
            echo "Installing for Arch-based distro..."
            sudo pacman -S --noconfirm ffmpeg python ncurses cargo
            ;;
        suse)
            echo "Installing for openSUSE..."
            sudo zypper install -y ffmpeg python3-devel ncurses-devel cargo
            ;;
        termux)
            echo "Installing for Termux (Android)..."
            pkg update
            pkg install -y python ffmpeg libiconv rust clang
            ;;
        *)
            echo "Unknown OS. Trying to install with pip and cargo..."
            ;;
    esac

    # Check if python3 is available
    if ! command -v python3 &> /dev/null; then
        echo "Python3 not found. Please install Python 3.8+ manually."
        exit 1
    fi

    # Check if cargo is available
    if ! command -v cargo &> /dev/null; then
        echo "Cargo not found. Installing Rust..."
        curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
        source "$HOME/.cargo/env"
    fi
}

# Install tplay
install_tplay() {
    echo ""
    echo "Installing tplay..."

    if command -v tplay &> /dev/null; then
        echo "tplay already installed: $(tplay --version 2>/dev/null || echo 'version unknown')"
    else
        cargo install tplay
    fi
}

# Create launcher script
create_launcher() {
    echo ""
    echo "Creating launcher script..."

    LAUNCHER_DIR="$HOME/.local/bin"
    mkdir -p "$LAUNCHER_DIR"

    # Get the directory where this script is located
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    LAUNCHER_PATH="$LAUNCHER_DIR/amp"

    # Create launcher
    cat > "$LAUNCHER_PATH" << EOF
#!/bin/bash
cd "$SCRIPT_DIR"
python3 "$SCRIPT_DIR/amp.py" "\$@"
EOF

    chmod +x "$LAUNCHER_PATH"

    # Add to PATH if not already there
    if [[ ":$PATH:" != *":$LAUNCHER_DIR:"* ]]; then
        echo ""
        echo "NOTE: Add $LAUNCHER_DIR to your PATH if not already added."
        echo "Add this line to your ~/.bashrc or ~/.zshrc:"
        echo "  export PATH=\"\$PATH:$LAUNCHER_DIR\""
    fi

    echo "Launcher created at: $LAUNCHER_PATH"
}

# Main
install_deps
install_tplay
create_launcher

echo ""
echo "======================================"
echo "  Installation Complete!"
echo "======================================"
echo ""
echo "Run 'amp' to start the player."
echo "Make sure ~/.local/bin is in your PATH."
echo ""