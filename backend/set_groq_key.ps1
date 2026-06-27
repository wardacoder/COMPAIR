# PowerShell script to set Groq API key
# Usage: .\set_groq_key.ps1

Write-Host "🔑 Groq API Key Setup" -ForegroundColor Cyan
Write-Host ""

# Check if key is already set
if ($env:GROQ_API_KEY) {
    Write-Host "Current API key: $($env:GROQ_API_KEY.Substring(0, [Math]::Min(10, $env:GROQ_API_KEY.Length)))..." -ForegroundColor Yellow
    $overwrite = Read-Host "Key already set. Overwrite? (y/n)"
    if ($overwrite -ne 'y') {
        Write-Host "Keeping existing key." -ForegroundColor Green
        exit
    }
}

Write-Host "1. Get your free API key from: https://console.groq.com/keys" -ForegroundColor Yellow
Write-Host "2. Paste your API key below (it should start with 'gsk_')" -ForegroundColor Yellow
Write-Host ""

$apiKey = Read-Host "Enter your Groq API key" -AsSecureString
$apiKeyPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
    [Runtime.InteropServices.Marshal]::SecureStringToBSTR($apiKey)
)

if ($apiKeyPlain -match '^gsk_') {
    $env:GROQ_API_KEY = $apiKeyPlain
    Write-Host ""
    Write-Host "✅ API key set successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "To make it permanent, add this to your PowerShell profile:" -ForegroundColor Yellow
    Write-Host "`$env:GROQ_API_KEY = '$apiKeyPlain'" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Or run the client now with:" -ForegroundColor Yellow
    Write-Host "python grok_mcp_client.py" -ForegroundColor Cyan
} else {
    Write-Host ""
    Write-Host "❌ Invalid API key format. Should start with 'gsk_'" -ForegroundColor Red
    Write-Host "Get your key from: https://console.groq.com/keys" -ForegroundColor Yellow
}






