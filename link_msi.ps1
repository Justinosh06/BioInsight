# Build MSI manually
$wixBin = "C:\Program Files (x86)\WiX Toolset v3.14\bin"
$staging = "C:\Users\justi\OneDrive\Documents\BioInsight\dist\staging"
$output = "C:\Users\justi\OneDrive\Documents\BioInsight\dist\BioInsight-v1.0.0.msi"

Write-Host "Linking MSI..."
& "$wixBin\light.exe" "$staging\Product.wixobj" -ext "$wixBin\WixUIExtension.dll" -out "$output" -sval 2>&1 | Tee-Object -FilePath "C:\Users\justi\OneDrive\Documents\BioInsight\wix_link.log"

if (Test-Path $output) {
    Write-Host "SUCCESS: MSI created at $output"
    Get-Item $output | Select-Object Name, LastWriteTime, @{N='SizeMB';E={[math]::Round($_.Length/1MB,2)}}
} else {
    Write-Host "FAILED: Check wix_link.log for errors"
}
