Write-Host "Copying .env file to VPS..."
# scp .env contabo.vps:/project/my-kink-is-karma/.env

# if ($LASTEXITCODE -eq 0) {
#     Write-Host "✅ Successfully copied .env file to VPS"
# } else {
#     Write-Host "❌ Failed to copy .env file to VPS"
#     exit 1
# }