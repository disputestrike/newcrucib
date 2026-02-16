#!/bin/bash
set -e

echo "=== Setting up CrucibAI ==="

echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r backend/requirements.txt

echo "Installing Node.js dependencies..."
cd frontend
npm install --legacy-peer-deps
npm run build
cd ..

echo "=== Setup complete ==="
