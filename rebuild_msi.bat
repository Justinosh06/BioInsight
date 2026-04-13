@echo off
cd /d "C:\Users\justi\OneDrive\Documents\BioInsight"
echo [1/3] Cleaning old files...
rmdir /s /q dist\staging 2>nul
del /f /q dist\BioInsight-v1.0.0.msi 2>nul
echo [2/3] Building MSI...
python build_msi_v5.py
echo [3/3] Done!
pause
