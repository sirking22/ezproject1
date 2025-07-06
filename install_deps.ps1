$ErrorActionPreference = "Continue"
$ProgressPreference = "Continue"

$packages = @(
    "notion-client==2.2.1",
    "python-telegram-bot==20.8",
    "openai==1.12.0",
    "python-dotenv==1.0.1",
    "aiohttp==3.12.7",
    "pytest==8.0.2",
    "pytest-asyncio==0.23.5",
    "pytest-cov==4.1.0"
)

foreach ($package in $packages) {
    Write-Host "Installing $package..."
    Start-Process -FilePath "pip" -ArgumentList "install", $package -NoNewWindow -Wait -PassThru
}

Write-Host "Installing pydantic with build tools..."
Start-Process -FilePath "pip" -ArgumentList "install", "--no-cache-dir", "pydantic==2.6.3" -NoNewWindow -Wait -PassThru 