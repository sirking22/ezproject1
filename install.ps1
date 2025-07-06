$ErrorActionPreference = "Continue"
$ProgressPreference = "Continue"

Write-Host "Installing package in development mode..."
Start-Process -FilePath "pip" -ArgumentList "install", "-e", "." -NoNewWindow -Wait -PassThru

Write-Host "Running tests..."
Start-Process -FilePath "python" -ArgumentList "-m", "pytest", "-v" -NoNewWindow -Wait -PassThru 