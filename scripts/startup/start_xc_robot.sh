#!/bin/bash
echo "Starting XC-ROBOT GUI on Darwin..."
cd "$(dirname "$0")/../.."
source ./venv/bin/activate
python3 scripts/startup/start_gui.py
