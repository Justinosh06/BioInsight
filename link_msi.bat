@echo off
echo Linking MSI...
"C:\Program Files (x86)\WiX Toolset v3.14\bin\light.exe" "C:\Users\justi\OneDrive\Documents\BioInsight\dist\staging\Product.wixobj" -ext "C:\Program Files (x86)\WiX Toolset v3.14\bin\WixUIExtension.dll" -out "C:\Users\justi\OneDrive\Documents\BioInsight\dist\BioInsight-v1.0.0.msi" -sval > link.log 2>&1
if %ERRORLEVEL% EQU 0 (
    echo SUCCESS: MSI created
) else (
    echo FAILED: Check link.log
)
type link.log
pause
