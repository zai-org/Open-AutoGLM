$PlatformTools = Join-Path $PSScriptRoot "platform-tools"
$Env:PATH = "$PlatformTools;$Env:PATH"
$Env:PYTHONIOENCODING = "utf-8"

# Configuration
$BaseUrl = "https://api.z.ai/api/paas/v4"
$Model = "autoglm-phone-multilingual"
$ApiKey = "PASTE_YOUR_Z_AI_API_KEY_HERE"

Write-Host "Checking for functionality..." -ForegroundColor Cyan
adb devices

Write-Host "Starting Open-AutoGLM with Z.ai..." -ForegroundColor Green
# Pass defaults if not overridden, but allow user arguments to take precedence if valid
# Simplified approach: We construct the command string with our defaults
# If the user provides arguments, we append them. 
# Note: main.py uses argparse. 

$ScriptArgs = @("--base-url", $BaseUrl, "--model", $Model, "--apikey", $ApiKey, "--connect", "100.67.146.75:5555") + $args

python -u main.py @ScriptArgs
