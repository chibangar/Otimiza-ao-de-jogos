#!/bin/bash

# Verificar se está autenticado
gh auth status

if [ $? -ne 0 ]; then
    echo "⚠️ Execute primeiro: gh auth login"
    exit 1
fi

# Criar release v3.0.0
gh release create \
    --yes \
    --prerelease=false \
    v3.0.0 \
    --title "Midnight Optimizer v3.0 — Glassmorphism Premium Release 🌙✨" \
    -F RELEASE_NOTES.md

echo ""
echo "✅ Release v3.0 publicada!"
