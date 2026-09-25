# ==============================================================================
# Midnight Optimizer — Script de Publicação de Nova Versão
# Cria a tag e envia para o GitHub, ativando a compilação automática na Release.
# ==============================================================================

param(
    [string]$Version = ""
)

$ErrorActionPreference = "Stop"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host " 🚀 Midnight Optimizer — Publicador de Nova Versão" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Obter versão atual do package.json
$pkgPath = Join-Path $PSScriptRoot "package.json"
$currentVer = "3.1.0"
if (Test-Path $pkgPath) {
    try {
        $pkg = Get-Content $pkgPath -Raw | ConvertFrom-Json
        $currentVer = $pkg.version
    } catch {}
}

# Se não foi fornecida versão, perguntar
if (-not $Version) {
    Write-Host "Versão atual detetada: v$currentVer" -ForegroundColor Yellow
    $suggested = "v3.1.0"
    $inputVer = Read-Host "Indica a nova versão (ex: $suggested ou prime Enter para $suggested)"
    if ([string]::IsNullOrWhiteSpace($inputVer)) {
        $Version = $suggested
    } else {
        $Version = $inputVer.Trim()
    }
}

# Normalizar tag (garantir prefixo 'v')
if (-not $Version.StartsWith("v")) {
    $cleanVer = $Version
    $tagVer = "v$Version"
} else {
    $cleanVer = $Version.Substring(1)
    $tagVer = $Version
}

Write-Host ""
Write-Host "A preparar release $tagVer (versão interna: $cleanVer)..." -ForegroundColor Green

# 2. Atualizar ficheiros de versão
Write-Host "[1/4] A atualizar ficheiros de versão..." -ForegroundColor Gray

# package.json
if (Test-Path $pkgPath) {
    $pkgContent = Get-Content $pkgPath -Raw
    $pkgContent = $pkgContent -replace '"version":\s*"[^"]+"', "`"version`": `"$cleanVer`""
    Set-Content -Path $pkgPath -Value $pkgContent -Encoding UTF8
}

# app.py
$appPath = Join-Path $PSScriptRoot "app.py"
if (Test-Path $appPath) {
    $appContent = Get-Content $appPath -Raw
    $appContent = $appContent -replace 'APP_VERSION\s*=\s*"[^"]+"', "APP_VERSION = `"$cleanVer`""
    Set-Content -Path $appPath -Value $appContent -Encoding UTF8
}

# 3. Git commit e tag
Write-Host "[2/4] A registar alterações no Git..." -ForegroundColor Gray
git add .
$status = git status --porcelain
if ($status) {
    git commit -m "Release $tagVer: Nova versão com interface profissional e melhorias de desempenho"
} else {
    Write-Host "Sem ficheiros alterados pendentes para commit." -ForegroundColor DarkGray
}

# Verificar se a tag já existe localmente
$existingTag = git tag -l $tagVer
if ($existingTag) {
    Write-Host "Aviso: A tag $tagVer já existia localmente. A substituir..." -ForegroundColor Yellow
    git tag -d $tagVer
}

Write-Host "[3/4] A criar tag Git $tagVer..." -ForegroundColor Gray
git tag -a $tagVer -m "Release $tagVer"

# 4. Git push para o GitHub
Write-Host "[4/4] A enviar commits e tag para o GitHub (origin)..." -ForegroundColor Green
git push origin main
git push origin $tagVer

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host " 🎉 Tag $tagVer enviada com sucesso para o GitHub!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "O GitHub Actions começou automaticamente a:" -ForegroundColor Cyan
Write-Host "  1. Compilar o executável MidnightOptimizer.exe (Windows 64-bit)"
Write-Host "  2. Empacotar o ficheiro ZIP de distribuição"
Write-Host "  3. Publicar a Release oficial com as notas de versão e downloads"
Write-Host ""
Write-Host "Podes acompanhar o progresso em:" -ForegroundColor Yellow
Write-Host "  https://github.com/chibangar/Otimiza-ao-de-jogos/actions"
Write-Host "E ver as tuas releases em:" -ForegroundColor Yellow
Write-Host "  https://github.com/chibangar/Otimiza-ao-de-jogos/releases"
Write-Host ""
