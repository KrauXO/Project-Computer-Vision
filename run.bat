@echo off
title Smart Inventory Kamera Sekre HMIF UNDIP
echo ==========================================================
echo   SMART INVENTORY KAMERA SEKRE HMIF UNDIP (EKOBIS 2026)
echo ==========================================================
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" main.py
) else (
    python main.py
)
pause

