# [CREATE] PowerShell script to install Cursor IDE settings
# Purpose: Automatically copy settings to Cursor user settings directory
# Agent: Composer
# Timestamp: 2025-12-05T01:35:00Z

Write-Host "🚀 Installing Cursor IDE Settings for Agents.MD Protocol" -ForegroundColor Cyan
Write-Host ""

# Get Cursor user settings directory
$cursorSettingsPath = "$env:APPDATA\Cursor\User\settings.json"
$cursorSnippetsPath = "$env:APPDATA\Cursor\User\python.code-snippets"
$templatePath = Join-Path $PSScriptRoot "cursor-user-settings-template.json"
$snippetsPath = Join-Path $PSScriptRoot ".vscode\python.code-snippets"

# Check if template exists
if (-not (Test-Path $templatePath)) {
    Write-Host "❌ Template file not found: $templatePath" -ForegroundColor Red
    exit 1
}

# Create Cursor User directory if it doesn't exist
$cursorUserDir = Split-Path $cursorSettingsPath -Parent
if (-not (Test-Path $cursorUserDir)) {
    Write-Host "📁 Creating Cursor User directory..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $cursorUserDir -Force | Out-Null
}

# Backup existing settings if they exist
if (Test-Path $cursorSettingsPath) {
    $backupPath = "$cursorSettingsPath.backup.$(Get-Date -Format 'yyyyMMdd-HHmmss')"
    Write-Host "💾 Backing up existing settings to: $backupPath" -ForegroundColor Yellow
    Copy-Item $cursorSettingsPath $backupPath
}

# Merge settings (if existing file, merge; otherwise create new)
if (Test-Path $cursorSettingsPath) {
    Write-Host "🔄 Merging with existing settings..." -ForegroundColor Yellow

    # Read existing settings
    $existingSettings = Get-Content $cursorSettingsPath -Raw | ConvertFrom-Json
    $templateSettings = Get-Content $templatePath -Raw | ConvertFrom-Json

    # Merge (template settings override existing)
    $mergedSettings = $existingSettings | ConvertTo-Json -Depth 10 | ConvertFrom-Json
    $templateSettings.PSObject.Properties | ForEach-Object {
        $mergedSettings | Add-Member -MemberType NoteProperty -Name $_.Name -Value $_.Value -Force
    }

    # Write merged settings
    $mergedSettings | ConvertTo-Json -Depth 10 | Set-Content $cursorSettingsPath
    Write-Host "✅ Settings merged successfully!" -ForegroundColor Green
} else {
    Write-Host "📝 Creating new settings file..." -ForegroundColor Yellow
    Copy-Item $templatePath $cursorSettingsPath
    Write-Host "✅ Settings file created!" -ForegroundColor Green
}

# Copy snippets file
if (Test-Path $snippetsPath) {
    Write-Host "📋 Copying Python snippets..." -ForegroundColor Yellow
    Copy-Item $snippetsPath $cursorSnippetsPath -Force
    Write-Host "✅ Snippets installed!" -ForegroundColor Green
} else {
    Write-Host "⚠️  Snippets file not found: $snippetsPath" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "✅ Installation complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📍 Settings location: $cursorSettingsPath" -ForegroundColor Cyan
Write-Host "📍 Snippets location: $cursorSnippetsPath" -ForegroundColor Cyan
Write-Host ""
Write-Host "🔀 Git Configuration Note:" -ForegroundColor Yellow
Write-Host "   All branches are LOCAL-ONLY by default (Agents.MD Protocol)" -ForegroundColor White
Write-Host "   Use 'git branch --unset-upstream' if upstream tracking is set" -ForegroundColor White
Write-Host ""
Write-Host "� Git Configuration Note:" -ForegroundColor Yellow
Write-Host "   All branches are LOCAL-ONLY by default (Agents.MD Protocol)" -ForegroundColor White
Write-Host "   Use 'git branch --unset-upstream' if upstream tracking is set" -ForegroundColor White
Write-Host ""
Write-Host "�🔄 Please reload Cursor IDE for changes to take effect:" -ForegroundColor Yellow
Write-Host "   Press Ctrl+Shift+P → 'Developer: Reload Window'" -ForegroundColor White
Write-Host ""
