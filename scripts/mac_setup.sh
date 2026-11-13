#!/usr/bin/env bash
# One-time setup of the video studio on a Mac (Apple Silicon or Intel).
# Safe to run again: it skips anything already installed.
#
# Paste into Terminal:
#   curl -fsSL https://raw.githubusercontent.com/bluebydesignz-gif/bettergitjoe/claude/barber-reel/scripts/mac_setup.sh | bash
#
# Installs: Homebrew, Node, ffmpeg, Python, git, yt-dlp, GitHub CLI, Claude Code,
# then puts the studio in ~/VideoStudio with its tools and a Python env for
# faster-whisper (speech-to-text, works on the Mac because Hugging Face is reachable).
set -euo pipefail

STUDIO="$HOME/VideoStudio"
REPO="https://github.com/bluebydesignz-gif/bettergitjoe.git"
BRANCH="claude/barber-reel"

say() { printf '\n\033[1;33m==> %s\033[0m\n' "$*"; }

# 1. Homebrew (asks you to press Return, then your Mac password; typing it shows nothing, that is normal)
if ! command -v brew >/dev/null 2>&1; then
  say "Installing Homebrew: press Return, then type your Mac password when asked"
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)" </dev/tty
fi
if [[ -x /opt/homebrew/bin/brew ]]; then BREW=/opt/homebrew/bin/brew; else BREW=/usr/local/bin/brew; fi
eval "$("$BREW" shellenv)"
grep -q 'brew shellenv' "$HOME/.zprofile" 2>/dev/null || echo "eval \"\$($BREW shellenv)\"" >>"$HOME/.zprofile"

# 2. Command-line tools
say "Installing Node, ffmpeg, Python, git, yt-dlp, GitHub CLI"
brew install node ffmpeg python git yt-dlp gh

# 3. Claude Code
if ! command -v claude >/dev/null 2>&1; then
  say "Installing Claude Code"
  curl -fsSL https://claude.ai/install.sh | bash
fi
grep -q '.local/bin' "$HOME/.zprofile" 2>/dev/null || echo 'export PATH="$HOME/.local/bin:$PATH"' >>"$HOME/.zprofile"
export PATH="$HOME/.local/bin:$PATH"

# 4. The studio project
if [[ -d "$STUDIO/.git" ]]; then
  say "Updating $STUDIO"
  git -C "$STUDIO" fetch -q origin "$BRANCH"
  git -C "$STUDIO" checkout -q "$BRANCH"
  git -C "$STUDIO" pull -q --ff-only origin "$BRANCH" || echo "  (has local changes, left as is)"
else
  say "Downloading the studio to $STUDIO"
  git clone -q -b "$BRANCH" "$REPO" "$STUDIO"
fi
cd "$STUDIO"

say "Installing the video tools (Remotion etc.)"
npm ci
npx remotion browser ensure >/dev/null

say "Setting up Python for speech-to-text and the beat maker"
python3 -m venv .venv
.venv/bin/pip install -q --upgrade pip
.venv/bin/pip install -q faster-whisper numpy
grep -q 'VideoStudio/.venv' "$HOME/.zprofile" 2>/dev/null || echo "export PATH=\"$STUDIO/.venv/bin:\$PATH\"" >>"$HOME/.zprofile"

mkdir -p public/music out
.venv/bin/python -I scripts/make_beat.py public/music/beat.wav

say "Checking everything works (renders a 4-second test video)"
npx remotion render src/index.ts HelloStudio out/hello.mp4 --log=error

say "All set!"
cat <<'EOF'
Your studio is in the VideoStudio folder in your home folder.
To start working with Claude, open a NEW Terminal window and type:

    cd ~/VideoStudio && claude

Claude on your Mac can open files on your Desktop (like the inspo folder).
EOF
