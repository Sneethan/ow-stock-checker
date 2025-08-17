Write-Host "Starting Officeworks Price Tracker Bot..." -ForegroundColor Green
Write-Host ""

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python 3.8 or higher." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if requirements are installed
if (Test-Path "requirements.txt") {
    Write-Host "✓ Requirements file found" -ForegroundColor Green
} else {
    Write-Host "❌ Requirements file not found" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if .env file exists
if (Test-Path ".env") {
    Write-Host "✓ Environment file found" -ForegroundColor Green
} else {
    Write-Host "⚠️  .env file not found. Please copy env.example to .env and add your Discord bot token." -ForegroundColor Yellow
    Write-Host "   You can still run the bot, but it will fail without the token." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Starting bot..." -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop the bot" -ForegroundColor Yellow
Write-Host ""

try {
    python bot.py
} catch {
    Write-Host "❌ Error running bot: $_" -ForegroundColor Red
}

Read-Host "Press Enter to exit"
