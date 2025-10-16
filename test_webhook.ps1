# Webhook Test Script for Vogent Integration
# This script tests your webhook endpoint to ensure it's working correctly

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "  Vogent Webhook Test Script" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check if Flask app is running
Write-Host "Step 1: Checking if Flask app is running on port 5000..." -ForegroundColor Yellow
try {
    $localTest = Invoke-WebRequest -Uri "http://localhost:5000/health" -Method GET -ErrorAction SilentlyContinue
    Write-Host "✅ Flask app is running!" -ForegroundColor Green
} catch {
    Write-Host "❌ Flask app is NOT running on port 5000" -ForegroundColor Red
    Write-Host "   Please start it first with: python vogent_transcript_automation.py" -ForegroundColor Yellow
    exit
}

Write-Host ""

# Step 2: Test local webhook endpoint
Write-Host "Step 2: Testing local webhook endpoint..." -ForegroundColor Yellow
$testPayload = @{
    event = "test"
    payload = @{
        dial_id = "test-webhook-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
    }
} | ConvertTo-Json

try {
    $response = Invoke-WebRequest -Uri "http://localhost:5000/webhook/vogent" `
        -Method POST `
        -ContentType "application/json" `
        -Body $testPayload `
        -ErrorAction Stop
    
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Local webhook endpoint is responding!" -ForegroundColor Green
        Write-Host "   Status: $($response.StatusCode)" -ForegroundColor Gray
    }
} catch {
    Write-Host "❌ Local webhook test failed: $_" -ForegroundColor Red
    exit
}

Write-Host ""

# Step 3: Check if ngrok is running
Write-Host "Step 3: Checking for ngrok tunnel..." -ForegroundColor Yellow
try {
    $ngrokApi = Invoke-RestMethod -Uri "http://localhost:4040/api/tunnels" -ErrorAction Stop
    $publicUrl = $ngrokApi.tunnels | Where-Object { $_.proto -eq "https" } | Select-Object -First 1 -ExpandProperty public_url
    
    if ($publicUrl) {
        Write-Host "✅ ngrok is running!" -ForegroundColor Green
        Write-Host "   Public URL: $publicUrl" -ForegroundColor Gray
        Write-Host ""
        Write-Host "==================================================" -ForegroundColor Green
        Write-Host "  WEBHOOK URL TO SET IN VOGENT:" -ForegroundColor Green
        Write-Host "==================================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "  $publicUrl/webhook/vogent" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "==================================================" -ForegroundColor Green
        Write-Host ""
        
        # Step 4: Test via ngrok URL
        Write-Host "Step 4: Testing webhook via ngrok URL..." -ForegroundColor Yellow
        try {
            $ngrokResponse = Invoke-WebRequest -Uri "$publicUrl/webhook/vogent" `
                -Method POST `
                -ContentType "application/json" `
                -Body $testPayload `
                -ErrorAction Stop
            
            if ($ngrokResponse.StatusCode -eq 200) {
                Write-Host "✅ ngrok webhook test successful!" -ForegroundColor Green
                Write-Host "   Check vogent_automation.log for the webhook entry" -ForegroundColor Gray
            }
        } catch {
            Write-Host "❌ ngrok webhook test failed: $_" -ForegroundColor Red
        }
    } else {
        Write-Host "❌ No HTTPS tunnel found" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ ngrok is NOT running" -ForegroundColor Red
    Write-Host "   Please start it in a separate terminal with: .\ngrok http 5000" -ForegroundColor Yellow
    Write-Host "   Then run this test script again" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "  Summary:" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "1. Flask app must be running: python vogent_transcript_automation.py"
Write-Host "2. ngrok must be running: .\ngrok http 5000"
Write-Host "3. Set the webhook URL in Vogent dashboard"
Write-Host "4. The URL format is: https://YOUR-SUBDOMAIN.ngrok.io/webhook/vogent"
Write-Host ""
