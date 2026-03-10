param(
    [Parameter(Mandatory=$true)][string]$RepoName,
    [string]$Owner,
    [switch]$Private
)

if (-not $env:GITHUB_TOKEN) {
    Write-Error "GITHUB_TOKEN is not set"
    exit 1
}

$Headers = @{
  "Authorization" = "token $($env:GITHUB_TOKEN)"
  "Accept"        = "application/vnd.github+json"
}
$Api = "https://api.github.com"
$Payload = @{ name = $RepoName; private = $Private.IsPresent } | ConvertTo-Json

if ($Owner) {
    Invoke-RestMethod -Method Post -Uri "$Api/orgs/$Owner/repos" -Headers $Headers -Body $Payload | Out-Null
    $remoteUrl = "https://github.com/$Owner/$RepoName.git"
} else {
    $me = Invoke-RestMethod -Method Get -Uri "$Api/user" -Headers $Headers
    Invoke-RestMethod -Method Post -Uri "$Api/user/repos" -Headers $Headers -Body $Payload | Out-Null
    $remoteUrl = "https://github.com/$($me.login)/$RepoName.git"
}

if (-not (Test-Path ".git")) { git init | Out-Null }
git add .
git commit -m "Initial commit" | Out-Null
git branch -M main | Out-Null

try {
  git remote get-url origin | Out-Null
  git remote set-url origin $remoteUrl | Out-Null
} catch {
  git remote add origin $remoteUrl | Out-Null
}

git push -u origin main

