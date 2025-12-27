# Run Phone Agent
# Make sure:
# 1. SSH tunnel is active (keep that terminal open)
# 2. WebDriverAgent is running on your Mac

param(
    [string]$Task = "Open Safari and search for iPhone tips",
    [string]$BaseUrl = "https://api.z.ai/api/paas/v4",
    [string]$Model = "autoglm-phone-multilingual",
    [string]$ApiKey = ""
)

Write-Host "Running Phone Agent..." -ForegroundColor Green
Write-Host "Task: $Task" -ForegroundColor Yellow
Write-Host "Model Service: $BaseUrl" -ForegroundColor Cyan
Write-Host ""

if ($ApiKey -eq "") {
    Write-Host "ERROR: API key required!" -ForegroundColor Red
    Write-Host "Usage: .\run_phone_agent.ps1 -Task 'Your task' -ApiKey 'your-api-key'" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Cloud service options:" -ForegroundColor Yellow
    Write-Host "  - z.ai: https://docs.z.ai/api-reference/introduction" -ForegroundColor Cyan
    Write-Host "  - Novita AI: https://novita.ai/models/model-detail/zai-org-autoglm-phone-9b-multilingual" -ForegroundColor Cyan
    Write-Host "  - Parasail: https://www.saas.parasail.io/serverless?name=auto-glm-9b-multilingual" -ForegroundColor Cyan
    exit 1
}

python ios.py `
    --wda-url http://localhost:8100 `
    --base-url $BaseUrl `
    --model $Model `
    --api-key $ApiKey `
    $Task

