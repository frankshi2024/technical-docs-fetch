#!/usr/bin/env bash
# install-gitee.sh — one-liner installer for technical-docs-fetch (via Gitee mirror)
# Usage: curl -fsSL https://gitee.com/frankshi2024/technical-docs-fetch/raw/main/install-gitee.sh | bash

set -euo pipefail

REPO="https://gitee.com/frankshi2024/technical-docs-fetch.git"
SKILL_DIRS=(
    "${HOME}/.config/agents/skills/technical-docs-fetch"
    "${HOME}/.agents/skills/technical-docs-fetch"
)
SKILL_URL="https://gitee.com/frankshi2024/technical-docs-fetch/raw/main/skill/SKILL.md"

# Old skill dirs from previous versions (named nic2markdown)
OLD_SKILL_DIRS=(
    "${HOME}/.config/agents/skills/nic2markdown"
    "${HOME}/.agents/skills/nic2markdown"
)

echo "====================================="
echo "  technical-docs-fetch installer"
echo "====================================="
echo ""

# Check prerequisites
if ! command -v uv &>/dev/null; then
    echo "[ERROR] uv is required but not installed."
    echo "  Install it: https://docs.astral.sh/uv/#installation"
    exit 1
fi

echo "[1/3] Installing technical-docs-fetch CLI (via uv tool install)..."
uv tool install "git+${REPO}" --force

echo ""
echo "[2/3] Cleaning up old nic2markdown skill directories..."
found_old=false
for OLD_DIR in "${OLD_SKILL_DIRS[@]}"; do
    if [ -d "${OLD_DIR}" ]; then
        found_old=true
        echo "  Found: ${OLD_DIR}"
    fi
done

if [ "${found_old}" = true ]; then
    read -rp "  Remove old nic2markdown skill directories? [y/N] " answer
    if [ "${answer}" = "y" ] || [ "${answer}" = "Y" ]; then
        for OLD_DIR in "${OLD_SKILL_DIRS[@]}"; do
            if [ -d "${OLD_DIR}" ]; then
                rm -rf "${OLD_DIR}"
                echo "  Removed: ${OLD_DIR}"
            fi
        done
    else
        echo "  Skipped."
    fi
else
    echo "  None found."
fi

echo ""
echo "[3/3] Installing agent skill..."
for SKILL_DIR in "${SKILL_DIRS[@]}"; do
    mkdir -p "${SKILL_DIR}"
    curl -fsSL "${SKILL_URL}" -o "${SKILL_DIR}/SKILL.md"
    echo "  -> ${SKILL_DIR}/SKILL.md"
done

echo ""
echo "====================================="
echo "  Installation complete!"
echo "====================================="
echo ""
echo "Try it out:"
echo "  technical-docs-fetch --help"
echo "  technical-docs-fetch https://soc.ustc.edu.cn/COD/lab5/"
