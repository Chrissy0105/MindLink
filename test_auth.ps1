# test_auth.ps1
Write-Host "Testing Authentication Endpoints..." -ForegroundColor Green

# Generate random test data to avoid duplicates
$randomId = Get-Random -Minimum 1000 -Maximum 9999
$testEmail = "testuser$randomId@example.com"
$testUsername = "testuser$randomId"
$testPassword = "TestPass123!"
$testPhone = "1876$((Get-Random -Minimum 1000000 -Maximum 9999999))"

Write-Host "Test User Details:" -ForegroundColor Yellow
Write-Host "Username: $testUsername"
Write-Host "Email: $testEmail"
Write-Host "Phone: $testPhone"

# 1. TEST REGISTRATION
Write-Host "`n1. Testing Registration..." -ForegroundColor Cyan

$registerBody = @{
    username = $testUsername
    email = $testEmail
    password = $testPassword
    telephone = $testPhone
} | ConvertTo-Json

Write-Host "Sending registration request..." -ForegroundColor Gray

try {
    $registerResponse = Invoke-RestMethod -Uri "http://localhost:5000/auth/register" `
        -Method Post `
        -ContentType "application/json" `
        -Body $registerBody
    
    Write-Host "✅ REGISTRATION SUCCESSFUL!" -ForegroundColor Green
    Write-Host "Response: $($registerResponse | ConvertTo-Json)" -ForegroundColor White
} catch {
    Write-Host "❌ REGISTRATION FAILED:" -ForegroundColor Red
    $errorDetails = $_.ErrorDetails.Message | ConvertFrom-Json
    Write-Host "Error: $($errorDetails.error)" -ForegroundColor Red
    if ($errorDetails.details) {
        Write-Host "Details: $($errorDetails.details)" -ForegroundColor Red
    }
}

# 2. TEST LOGIN
Write-Host "`n2. Testing Login..." -ForegroundColor Cyan

$loginBody = @{
    email = $testEmail
    password = $testPassword
} | ConvertTo-Json

Write-Host "Sending login request..." -ForegroundColor Gray

try {
    $loginResponse = Invoke-RestMethod -Uri "http://localhost:5000/auth/login" `
        -Method Post `
        -ContentType "application/json" `
        -Body $loginBody
    
    Write-Host "✅ LOGIN SUCCESSFUL!" -ForegroundColor Green
    $token = $loginResponse.access_token
    Write-Host "JWT Token Received: $($token.Substring(0, 50))..." -ForegroundColor Yellow
    
    # Store token for later use
    $global:AuthToken = $token
    
} catch {
    Write-Host "❌ LOGIN FAILED:" -ForegroundColor Red
    $errorDetails = $_.ErrorDetails.Message | ConvertFrom-Json
    Write-Host "Error: $($errorDetails.error)" -ForegroundColor Red
}

# 3. TEST PROTECTED CHAT ENDPOINT
if ($global:AuthToken) {
    Write-Host "`n3. Testing Protected Chat Endpoint..." -ForegroundColor Cyan
    
    $chatMessages = @(
        @{message = "I am feeling great today!"},
        @{message = "I feel a bit sad and lonely"},
        @{message = "I don't want to live anymore"}
    )
    
    foreach ($chatData in $chatMessages) {
        $jsonBody = $chatData | ConvertTo-Json
        Write-Host "Sending: $($chatData.message)" -ForegroundColor Gray
        
        try {
            $chatResponse = Invoke-RestMethod -Uri "http://localhost:5000/chat/message" `
                -Method Post `
                -ContentType "application/json" `
                -Headers @{ "Authorization" = "Bearer $global:AuthToken" } `
                -Body $jsonBody
            
            Write-Host "✅ Chat Response - Risk Level: $($chatResponse.risk_level)" -ForegroundColor Green
            if ($chatResponse.alert) {
                Write-Host "🚨 ALERT: $($chatResponse.alert)" -ForegroundColor Red
            }
            Write-Host ""
            
        } catch {
            Write-Host "❌ Chat Failed: $($_.Exception.Message)" -ForegroundColor Red
        }
    }
}

Write-Host "`n🎉 Authentication Testing Complete!" -ForegroundColor Green
if ($global:AuthToken) {
    Write-Host "Your JWT Token (for manual testing):" -ForegroundColor Yellow
 12
 3.0   Write-Host "$global:AuthToken" -ForegroundColor White
}