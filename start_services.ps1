# Start Services Script
# This script starts Flask webhook, ngrok, and transcript viewer

Write-Host ""
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "  Starting Vogent Automation Services" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# Check if Flask webhook is already running
Write-Host "[1/4] Checking Flask webhook..." -NoNewline
try {
    $null = Invoke-WebRequest -Uri "http://localhost:5000/health" -Method GET -TimeoutSec 2 -ErrorAction Stop
    Write-Host " [OK] Already Running" -ForegroundColor Green
    $flaskRunning = $true
} catch {
    Write-Host " [X] Not Running" -ForegroundColor Yellow
    $flaskRunning = $false
}

# Check if ngrok is already running
Write-Host "[2/4] Checking ngrok..." -NoNewline
try {
    $ngrokApi = Invoke-RestMethod -Uri "http://localhost:4040/api/tunnels" -TimeoutSec 2 -ErrorAction Stop
    $publicUrl = $ngrokApi.tunnels | Where-Object { $_.proto -eq "https" } | Select-Object -First 1 -ExpandProperty public_url
    
    if ($publicUrl) {
        Write-Host " [OK] Already Running" -ForegroundColor Green
        $ngrokRunning = $true
    } else {
        Write-Host " [X] No HTTPS tunnel" -ForegroundColor Yellow
        $ngrokRunning = $false
    }
} catch {
    Write-Host " [X] Not Running" -ForegroundColor Yellow
    $ngrokRunning = $false
}

# Check if viewer is already running
Write-Host "[3/4] Checking transcript viewer..." -NoNewline
try {
    $null = Invoke-WebRequest -Uri "http://localhost:8080" -Method GET -TimeoutSec 2 -ErrorAction Stop
    Write-Host " [OK] Already Running" -ForegroundColor Green
    $viewerRunning = $true
} catch {
    Write-Host " [X] Not Running" -ForegroundColor Yellow
    $viewerRunning = $false
}

Write-Host ""

# Start Flask if not running
if (-not $flaskRunning) {
    Write-Host "Starting Flask server..." -ForegroundColor Yellow
    Write-Host "Opening new terminal for Flask..." -ForegroundColor Gray
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; Write-Host 'Starting Flask...' -ForegroundColor Green; python vogent_transcript_automation.py"
    
    Write-Host "Waiting for Flask to start..." -NoNewline
    Start-Sleep -Seconds 3
    
    try {
        $null = Invoke-WebRequest -Uri "http://localhost:5000/health" -Method GET -TimeoutSec 5 -ErrorAction Stop
        Write-Host " [OK] Started!" -ForegroundColor Green
    } catch {
        Write-Host " [!] May need more time" -ForegroundColor Yellow
    }
    Write-Host ""
}

# Start ngrok if not running
if (-not $ngrokRunning) {
    Write-Host "Starting ngrok tunnel..." -ForegroundColor Yellow
    Write-Host "Opening new terminal for ngrok..." -ForegroundColor Gray
    
    # Check if ngrok exists in current directory
    if (Test-Path ".\ngrok.exe") {
        Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; Write-Host 'Starting ngrok...' -ForegroundColor Green; .\ngrok http 5000"
    } elseif (Test-Path ".\ngrok\ngrok.exe") {
        Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\ngrok'; Write-Host 'Starting ngrok...' -ForegroundColor Green; .\ngrok http 5000"
    } else {
        Write-Host " [X] ngrok.exe not found!" -ForegroundColor Red
        Write-Host "   Please download from: https://ngrok.com/download" -ForegroundColor Yellow
        Write-Host "   Or start manually: .\ngrok http 5000" -ForegroundColor Yellow
        exit
    }
    
    Write-Host "Waiting for ngrok to start..." -NoNewline
    Start-Sleep -Seconds 3
    
    try {
        $ngrokApi = Invoke-RestMethod -Uri "http://localhost:4040/api/tunnels" -TimeoutSec 5 -ErrorAction Stop
        $publicUrl = $ngrokApi.tunnels | Where-Object { $_.proto -eq "https" } | Select-Object -First 1 -ExpandProperty public_url
        Write-Host " [OK] Started!" -ForegroundColor Green
    } catch {
        Write-Host " [!] May need more time" -ForegroundColor Yellow
    }
    Write-Host ""
}

# Start transcript viewer if not running
if (-not $viewerRunning) {
    Write-Host "Starting transcript viewer..." -ForegroundColor Yellow
    Write-Host "Opening new terminal for viewer..." -ForegroundColor Gray
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; Write-Host 'Starting Transcript Viewer...' -ForegroundColor Green; Write-Host 'Server running on http://localhost:8080' -ForegroundColor Cyan; Write-Host ''; python transcript_viewer.py"
    
    Write-Host "Waiting for viewer to start..." -NoNewline
    Start-Sleep -Seconds 3
    
    try {
        $null = Invoke-WebRequest -Uri "http://localhost:8080" -Method GET -TimeoutSec 5 -ErrorAction Stop
        Write-Host " [OK] Started!" -ForegroundColor Green
    } catch {
        Write-Host " [!] May need more time" -ForegroundColor Yellow
    }
    Write-Host ""
}

# Display the webhook URL
Write-Host "[4/4] Getting webhook URL..." -ForegroundColor Yellow
Start-Sleep -Seconds 2

try {
    $ngrokApi = Invoke-RestMethod -Uri "http://localhost:4040/api/tunnels" -TimeoutSec 5 -ErrorAction Stop
    $publicUrl = $ngrokApi.tunnels | Where-Object { $_.proto -eq "https" } | Select-Object -First 1 -ExpandProperty public_url
    
    if ($publicUrl) {
        Write-Host ""
        Write-Host "==================================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "  [OK] SERVICES RUNNING!" -ForegroundColor Green
        Write-Host ""
        Write-Host "  YOUR WEBHOOK URL FOR VOGENT:" -ForegroundColor Green
        Write-Host ""
        Write-Host "  $publicUrl/webhook/vogent" -ForegroundColor Cyan -BackgroundColor Black
        Write-Host ""
        Write-Host "==================================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "COPY THIS URL TO VOGENT DASHBOARD WEBHOOK SETTINGS" -ForegroundColor Yellow
        Write-Host ""
        
        # Test the webhook
        Write-Host "Testing webhook..." -NoNewline
        $testPayload = @{
            event = "test"
            payload = @{ dial_id = "startup-test-$(Get-Date -Format 'HHmmss')" }
        } | ConvertTo-Json
        
        try {
            $response = Invoke-WebRequest -Uri "$publicUrl/webhook/vogent" `
                -Method POST `
                -ContentType "application/json" `
                -Body $testPayload `
                -TimeoutSec 10 `
                -ErrorAction Stop
            
            if ($response.StatusCode -eq 200) {
                Write-Host " [OK] Working!" -ForegroundColor Green
            }
        } catch {
            Write-Host " [!] Test failed (this is OK for fake test data)" -ForegroundColor Yellow
        }
        
        Write-Host ""
        Write-Host "TIP: Run .\get_webhook_url.ps1 anytime to see your current URL" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "TRANSCRIPT VIEWER: http://localhost:8080" -ForegroundColor Cyan
        Write-Host ""
        
    } else {
        Write-Host " [X] Could not get ngrok URL" -ForegroundColor Red
    }
} catch {
    Write-Host " [X] ngrok not responding" -ForegroundColor Red
    Write-Host "   Wait a few seconds and run: .\get_webhook_url.ps1" -ForegroundColor Yellow
}

Write-Host ""
