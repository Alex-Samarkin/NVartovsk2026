[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

$AuthorizationKey = "YTgxYTIyZjctNzAzYi00YWJkLWIwOGYtNzJjYTAzYjgyZGY3OmMxZjU4YzMyLTAyZDgtNDI2NS05YWU1LTA1MWNjZTM2ZTI2MQ=="

$Scope = "GIGACHAT_API_PERS"
if ([string]::IsNullOrWhiteSpace($AuthorizationKey)) {
    throw "GIGACHAT_AUTH_KEY environment variable is not set"
}

# Step 1: Get an access token.
$tokenHeaders = @{
    Authorization = "Basic $AuthorizationKey"
    RqUID = [guid]::NewGuid().ToString()
    Accept = "application/json"
}

try {
    $tokenResponse = Invoke-RestMethod `
        -Method Post `
        -Uri "https://ngw.devices.sberbank.ru:9443/api/v2/oauth" `
        -Headers $tokenHeaders `
        -ContentType "application/x-www-form-urlencoded" `
        -Body @{
            scope = $Scope
        }

    $token = $tokenResponse.access_token

    if ([string]::IsNullOrWhiteSpace($token)) {
        throw "The server did not return an access_token"
    }

    Write-Host "Access token received"
    Write-Host "Token length:" $token.Length

    Write-Host $token
}
catch {
    Write-Host "Token request failed:" $_.Exception.Message

    if ($_.Exception.Response) {
        Write-Host "HTTP status:" $_.Exception.Response.StatusCode.value__

        $reader = New-Object System.IO.StreamReader(
            $_.Exception.Response.GetResponseStream()
        )

        $errorBody = $reader.ReadToEnd()

        if ([string]::IsNullOrWhiteSpace($errorBody)) {
            Write-Host "The server returned an empty response body"
        }
        else {
            Write-Host "Server response:"
            Write-Host $errorBody
        }
    }

    exit 1
}

# Step 2: Prepare the chat request.
$chatHeaders = @{
    Authorization = "Bearer $token"
    Accept = "application/json"
    "Content-Type" = "application/json"
}

$requestBody = @{
    model = "GigaChat-3-Ultra"
    messages = @(
        @{
            role = "user"
            content = "Hello. Whats new in  the world and Russia?"
        }
    )
    stream = $false
} | ConvertTo-Json -Depth 10

# Step 3: Send the request using the newly received token.
try {
    $chatResponse = Invoke-RestMethod `
        -Method Post `
        -Uri "https://api.giga.chat/v1/chat/completions" `
        -Headers $chatHeaders `
        -Body $requestBody

    Write-Host ""
    Write-Host "GigaChat response:"
    Write-Host $chatResponse.choices[0].message.content
}
catch {
    Write-Host ""
    Write-Host "Chat request failed:" $_.Exception.Message

    if ($_.Exception.Response) {
        Write-Host "HTTP status:" $_.Exception.Response.StatusCode.value__

        $reader = New-Object System.IO.StreamReader(
            $_.Exception.Response.GetResponseStream()
        )

        $errorBody = $reader.ReadToEnd()

        if ([string]::IsNullOrWhiteSpace($errorBody)) {
            Write-Host "The server returned an empty response body"
        }
        else {
            Write-Host "Server response:"
            Write-Host $errorBody
        }
    }

    exit 1
}