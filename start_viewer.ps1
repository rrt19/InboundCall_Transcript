# Start Kyron Medical Transcript Viewer
# This script starts the web viewer for patient-assistant transcripts

Write-Host ""
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "  Kyron Medical - Transcript Viewer" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# Check if viewer is already running
Write-Host "Checking if viewer is running..." -NoNewline
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8080" -Method GET -TimeoutSec 2 -ErrorAction Stop
    Write-Host " [OK] Already running!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Viewer is already running at:" -ForegroundColor Yellow
    Write-Host "  http://localhost:8080" -ForegroundColor Cyan
    Write-Host ""
    
    # Ask if they want to open in browser
    $open = Read-Host "Open in browser? (Y/n)"
    if ($open -ne "n" -and $open -ne "N") {
        Start-Process "http://localhost:8080"
    }
    exit
} catch {
    Write-Host " [X] Not running" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Starting transcript viewer..." -ForegroundColor Yellow

# Start the viewer in a new window
Start-Process powershell -ArgumentList "-NoExit", "-Command", @"
cd '$PWD'
Write-Host '=====================================================' -ForegroundColor Cyan
Write-Host ' Kyron Medical - Patient-Assistant Transcript Viewer' -ForegroundColor Cyan
Write-Host '=====================================================' -ForegroundColor Cyan
Write-Host ''
Write-Host 'Starting server on port 8080...' -ForegroundColor Green
Write-Host ''
python transcript_viewer.py
"@

# Wait for it to start
Write-Host "Waiting for server to start..." -NoNewline
Start-Sleep -Seconds 3

# Check if it started
$started = $false
for ($i = 0; $i -lt 5; $i++) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8080" -Method GET -TimeoutSec 2 -ErrorAction Stop
        Write-Host " [OK] Started!" -ForegroundColor Green
        $started = $true
        break
    } catch {
        Start-Sleep -Seconds 1
    }
}

if (-not $started) {
    Write-Host " [!] Taking longer than expected" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Check the server window for any errors." -ForegroundColor Gray
    Write-Host "It should be starting on port 8080..." -ForegroundColor Gray
    Write-Host ""
    exit
}

Write-Host ""
Write-Host "==================================================" -ForegroundColor Green
Write-Host ""
Write-Host "  [OK] Kyron Medical Transcript Viewer is running!" -ForegroundColor Green
Write-Host ""
Write-Host "  Access at: http://localhost:8080" -ForegroundColor Cyan -BackgroundColor Black
Write-Host ""
Write-Host "==================================================" -ForegroundColor Green
Write-Host ""

# Open in browser
Write-Host "Opening in browser..." -ForegroundColor Yellow
Start-Sleep -Seconds 1
Start-Process "http://localhost:8080"

Write-Host ""
Write-Host "Viewer is running in the background window." -ForegroundColor Gray
Write-Host "Keep that window open to keep the viewer running." -ForegroundColor Gray
Write-Host ""
