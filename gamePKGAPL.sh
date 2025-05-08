#!/bin/bash
pyinstaller `
  --name "StairCase" `
  --onefile `
  --windowed `
  --add-data "graphics:graphics" `
  staircase_game\Menue.py

