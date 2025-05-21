#!/bin/bash
cd "$(dirname "$0")"

pyinstaller \
  --name "StairCase" \
  --windowed \
  --add-data "graphics:graphics" \
  --hidden-import=game_client \
  Front_Game_Client/Menue.py
