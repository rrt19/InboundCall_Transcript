# Quick: Get Your Webhook URL

Write-Host ""
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "  Getting Your Vogent Webhook URL" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# Check Flask
Write-Host "Checking Flask app..." -NoNewline
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5000/health" -Method GET -TimeoutSec 3 -ErrorAction Stop
    Write-Host " ✅ Running" -ForegroundColor Green
} catch {
    Write-Host " ❌ NOT Running" -ForegroundColor Red
    Write-Host ""
    Write-Host "START FLASK:" -ForegroundColor Yellow
    Write-Host "  python vogent_transcript_automation.py" -ForegroundColor White
    Write-Host ""
    Write-Host "Or run: .\start_services.ps1  (starts both Flask & ngrok)" -ForegroundColor Cyan
    Write-Host ""
    exit
}

# Check ngrok
Write-Host "Checking ngrok..." -NoNewline
try {
    $ngrokApi = Invoke-RestMethod -Uri "http://localhost:4040/api/tunnels" -TimeoutSec 2 -ErrorAction Stop
    $publicUrl = $ngrokApi.tunnels | Where-Object { $_.proto -eq "https" } | Select-Object -First 1 -ExpandProperty public_url
    
    if ($publicUrl) {
        Write-Host " ✅ Running" -ForegroundColor Green
        Write-Host ""
        Write-Host "==================================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "  YOUR WEBHOOK URL FOR VOGENT:" -ForegroundColor Green
        Write-Host ""
        Write-Host "  $publicUrl/webhook/vogent" -ForegroundColor Cyan -BackgroundColor Black
        Write-Host ""
        Write-Host "==================================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "Copy this URL and paste it in your Vogent webhook settings." -ForegroundColor Yellow
        Write-Host ""
        
        # Test it
        Write-Host "Testing webhook..." -NoNewline
        $testPayload = @{
            event = "test"
            payload = @{ dial_id = "test-$(Get-Date -Format 'HHmmss')" }
        } | ConvertTo-Json
        
        try {
            $response = Invoke-WebRequest -Uri "$publicUrl/webhook/vogent" `
                -Method POST `
                -ContentType "application/json" `
                -Body $testPayload `
                -TimeoutSec 5 `
                -ErrorAction Stop
            
            if ($response.StatusCode -eq 200) {
                Write-Host " ✅ Working!" -ForegroundColor Green
            }
        } catch {
            Write-Host " ⚠️ Test failed" -ForegroundColor Yellow
            Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Gray
        }
    } else {
        Write-Host " ❌ No HTTPS tunnel" -ForegroundColor Red
    }
} catch {
    Write-Host " ❌ NOT Running" -ForegroundColor Red
    Write-Host ""
    Write-Host "START NGROK:" -ForegroundColor Yellow
    Write-Host "  .\ngrok http 5000" -ForegroundColor White
    Write-Host ""
    Write-Host "Or run: .\start_services.ps1  (starts both Flask & ngrok)" -ForegroundColor Cyan
    Write-Host ""
}

Write-Host ""
