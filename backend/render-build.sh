#!/usr/bin/env bash
# Render build script for backend

set -e

echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Creating necessary directories..."
mkdir -p /tmp/uploads
mkdir -p /tmp/models
mkdir -p /tmp/temp

echo "Build complete!"
