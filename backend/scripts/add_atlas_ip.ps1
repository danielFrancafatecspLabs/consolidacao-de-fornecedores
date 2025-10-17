<#
Adds an IP address to MongoDB Atlas Project Access List using Atlas API.

Usage examples:
  # Using environment variables (recommended):
  $env:ATLAS_PUBLIC_KEY = 'YOUR_PUBLIC_KEY'
  $env:ATLAS_PRIVATE_KEY = 'YOUR_PRIVATE_KEY'
  $env:ATLAS_PROJECT_ID = 'YOUR_PROJECT_ID'
  .\add_atlas_ip.ps1

  # Or pass parameters directly:
  .\add_atlas_ip.ps1 -PublicKey 'PUB' -PrivateKey 'PRIV' -ProjectId 'PROJECT_ID' -Ip '24.239.160.133/32'

Notes:
- This script calls curl.exe with HTTP Digest auth. Ensure curl.exe is available (Windows 10+ includes it).
- Keep your API keys secret. Prefer environment variables.
#>

param(
    [string]$PublicKey = $env:ATLAS_PUBLIC_KEY,
    [string]$PrivateKey = $env:ATLAS_PRIVATE_KEY,
    [string]$ProjectId = $env:ATLAS_PROJECT_ID,
    [string]$Ip = '24.239.160.133/32'
)

if (-not $PublicKey) {
    $PublicKey = Read-Host 'Atlas Public Key (API)'
}
if (-not $PrivateKey) {
    $PrivateKey = Read-Host -AsSecureString 'Atlas Private Key (API)';
    $PrivateKey = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($PrivateKey))
}
if (-not $ProjectId) {
    $ProjectId = Read-Host 'Atlas Project ID (Group ID)'
}

if (-not $PublicKey -or -not $PrivateKey -or -not $ProjectId) {
    Write-Error 'PublicKey, PrivateKey and ProjectId are required.'
    exit 1
}

$uri = "https://cloud.mongodb.com/api/atlas/v1.0/groups/$ProjectId/accessList"

$payload = @{ ipAddress = $Ip; comment = "added via script" } | ConvertTo-Json -Compress

Write-Host "Adding IP $Ip to Atlas project $ProjectId..."

# Call curl.exe with digest auth
$args = @(
    '--digest',
    '-u', "${PublicKey}:${PrivateKey}",
    '-X', 'POST',
    $uri,
    '-H', 'Content-Type: application/json',
    '-d', $payload
)

try {
    $proc = Start-Process -FilePath 'curl.exe' -ArgumentList $args -NoNewWindow -Wait -PassThru -RedirectStandardOutput -RedirectStandardError
    $out = $proc.StandardOutput.ReadToEnd()
    $err = $proc.StandardError.ReadToEnd()
    if ($proc.ExitCode -eq 0) {
        Write-Host 'Resposta da API:'
        Write-Host $out
    } else {
        Write-Error "curl retornou código $($proc.ExitCode)"
        Write-Error $err
        Write-Host $out
    }
} catch {
    Write-Error "Falha ao executar curl: $_"
}
