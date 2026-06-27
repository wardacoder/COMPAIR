# COMPAIR Environment Setup Script
# This script helps you set up your .env file with the OpenAI API key

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "COMPAIR Environment Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if .env exists
if (-not (Test-Path .env)) {
    Write-Host "Creating .env file..." -ForegroundColor Yellow
    New-Item -Path .env -ItemType File -Force | Out-Null
}

# Check if OPENAI_API_KEY is already set
$envContent = Get-Content .env -ErrorAction SilentlyContinue
$hasOpenAIKey = $envContent | Select-String -Pattern "^OPENAI_API_KEY=" -Quiet

if ($hasOpenAIKey) {
    Write-Host "⚠️  OPENAI_API_KEY already exists in .env file" -ForegroundColor Yellow
    Write-Host ""
    $update = Read-Host "Do you want to update it? (y/n)"
    if ($update -ne "y" -and $update -ne "Y") {
        Write-Host "Skipping..." -ForegroundColor Gray
        exit
    }
    # Remove old OPENAI_API_KEY line
    $envContent = $envContent | Where-Object { $_ -notmatch "^OPENAI_API_KEY=" }
}

Write-Host ""
Write-Host "To get your OpenAI API key:" -ForegroundColor Green
Write-Host "1. Go to https://platform.openai.com/api-keys" -ForegroundColor White
Write-Host "2. Sign in or create an account" -ForegroundColor White
Write-Host "3. Click 'Create new secret key'" -ForegroundColor White
Write-Host "4. Copy the key (it starts with 'sk-...')" -ForegroundColor White
Write-Host ""

$apiKey = Read-Host "Enter your OpenAI API key (or press Enter to skip)"

if ([string]::IsNullOrWhiteSpace($apiKey)) {
    Write-Host ""
    Write-Host "⚠️  No API key provided. You can add it later by editing the .env file." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "To add it manually:" -ForegroundColor Cyan
    Write-Host "1. Open the .env file in a text editor" -ForegroundColor White
    Write-Host "2. Add this line: OPENAI_API_KEY=your_key_here" -ForegroundColor White
    Write-Host "3. Replace 'your_key_here' with your actual API key" -ForegroundColor White
    Write-Host ""
} else {
    # Add OPENAI_API_KEY to .env
    if ($envContent) {
        $envContent += "OPENAI_API_KEY=$apiKey"
        $envContent | Set-Content .env
    } else {
        "OPENAI_API_KEY=$apiKey" | Add-Content .env
    }
    
    Write-Host ""
    Write-Host "✅ OPENAI_API_KEY added to .env file!" -ForegroundColor Green
    Write-Host ""
}

# Check for other optional keys
Write-Host "Optional: Brave Search API Key (for real-time search data)" -ForegroundColor Cyan
Write-Host "Get it from: https://brave.com/search/api/" -ForegroundColor Gray
$braveKey = Read-Host "Enter Brave API key (or press Enter to skip)"

if (-not [string]::IsNullOrWhiteSpace($braveKey)) {
    $envContent = Get-Content .env
    $hasBraveKey = $envContent | Select-String -Pattern "^BRAVE_API_KEY=" -Quiet
    if ($hasBraveKey) {
        $envContent = $envContent | Where-Object { $_ -notmatch "^BRAVE_API_KEY=" }
    }
    $envContent += "BRAVE_API_KEY=$braveKey"
    $envContent | Set-Content .env
    Write-Host "✅ BRAVE_API_KEY added!" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Restart your backend server" -ForegroundColor White
Write-Host "2. The warning should disappear" -ForegroundColor White
Write-Host "3. Try comparing items again" -ForegroundColor White
Write-Host ""




