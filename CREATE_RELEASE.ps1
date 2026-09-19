# PowerShell script para criar release no GitHub
# Execute como Administrador ou com token configurado

$ErrorActionPreference = "Stop"
$url = "https://api.github.com/repos/chibangar/Otimiza-ao-de-jogos/releases"
$headers = @{
    "Authorization" = "token YOUR_GITHUB_TOKEN"  # Cole seu token aqui
    "Accept" = "application/vnd.github.v3+json"
}

# Ver se o usuário está logado no GitHub CLI
try {
    gh auth status | Select-String "logged in"
    
    if (-not (gh auth status | Select-String "logged in")) {
        Write-Host "⚠️ Usuário não logado. Execute: gh auth login" -ForegroundColor Yellow
    } else {
        # Criar release com token do CLI ou API
        $body = @{
            tag_name = "v3.0.0"
            name = "Midnight Optimizer v3.0 — Glassmorphism Premium Release 🌙✨"
            body = @'
## 🎉 Midnight Optimizer v3.0 — Design Moderno!

### ✨ Novidades Principais

#### 🎨 Glassmorphism Premium
- Efeitos de vidro fosco em todos os cards e painéis
- Background animado com partículas interativas  
- Transições fluidas e profissionais (300ms ease-out-expo)

#### 💫 15+ Animações Novas
- **Ripple effect** nos botões (onda expansiva ao clicar)
- **Hover smooth** com física de mola (ease-bounce)
- **Float animation** em ícones e badges
- **Shimmer effect** no fundo gradient
- **Glow pulses** em elementos ativos

#### 🚀 Performance Melhorada
- Transições otimizadas de 300ms
- Focus rings acessíveis para navegação por teclado
- High DPI optimizations (4K ready)
'@
            
        Write-Host "🌙 Criando Release v3.0 no GitHub..." -ForegroundColor Green
        
        # Fazer upload do release usando gh CLI
        $body | ConvertTo-Json | ForEach-Object { $_ }
    }
} catch {
    Write-Host "Erro: $_" -ForegroundColor Red
    Write-Host "💡 Dica: Execute 'gh release create v3.0.0' no PowerShell" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "📚 Para criar o release manualmente, execute:" -ForegroundColor Cyan
Write-Host "   1. gh auth login" 
Write-Host "   2. gh release create v3.0.0 --title \"Midnight Optimizer v3.0 — Glassmorphism Premium\" --notes-file RELEASE_NOTES.md"
