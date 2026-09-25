# Changelog

## [v3.2.4] - 2026-09-24

### 🚀 Motor de Atualização Interno Blindado (PowerShell In-App Updater)
- **Substituição do Script Batch Frágil por PowerShell Nativo**: O processo de substituição e reinício do executável agora é gerido por um script PowerShell assíncrono que contorna bloqueios de ficheiro do Windows, elimina o bug do comando `timeout` em processos ocultos e aplica a atualização de forma infalível.
- **Botão Dedicado 'Verificar Atualizações'**: Adicionado botão direto na barra lateral e na página de Sistema para procurar atualizações a qualquer momento sem ter de esperar pelo temporizador.
- **Feedback em Tempo Real**: Mensagens claras via toast a informar se a app já está na versão mais recente ou se há nova versão pronta para instalar com 1 clique.
- **Eliminação de Bloqueio por Erro Prévio**: O verificador de atualizações já não é interrompido caso uma atualização anterior tenha registado falha transitória.

## [v3.2.3] - 2026-09-24

### 🎮 Imagens Reais In-Game dos Bonecos & Armas do CS2 (Viewmodels)
- **Renders Autênticos do CS2**: Substituição das ilustrações abstratas por capturas e renders reais do CS2 no mapa crashz' Viewmodel Generator com céu azul limpo, nuvens e os braços/luvas táticas dos agentes do jogo empunhando a AK-47.
- **Visualização Fiel do Posicionamento**: Mostra com precisão fotográfica onde a arma e os braços do boneco ficam posicionados no ecrã para cada preset (Clássico Pro launders/crashz, Compacto Recuado, FOV Máximo Estendido, Centrado Quake/Doom, Padrão Valve Desktop e Minimalista).
- **Novo Preset Gangster Clássico**: Adicionado o icónico preset da comunidade com arma inclinada e elevada no ecrã.
- **Otimização de Imagens Ultraleves**: Imagens compactadas a ~100KB com nitidez total, mantendo o download rápido e leve.

## [v3.2.2] - 2026-09-24

### 🛠️ Correção de Sintaxe f-string para Python < 3.12 (pros.py)
- **Eliminação do Erro de Sintaxe**: Resolvido o erro `SyntaxError: f-string expression part cannot include a backslash` em `pros.py` nas funções `apply_crosshair_safe` e `apply_viewmodel_safe`.
- **Compatibilidade Total**: Remoção de caracteres de escape (`\n`) de dentro das expressões `{...}` de interpolação f-string, garantindo compatibilidade universal com todas as versões do Python e ambientes Windows de utilizador.

## [v3.2.1] - 2026-09-24

### 🛠️ Correção Crítica de Executável (Bundling de Módulos)
- **Correção de Crash de Inicialização**: Resolvido o erro `ModuleNotFoundError: No module named 'pros'` na versão compilada `MidnightOptimizer.exe`.
- **Compilação Determinística via Spec File**: O fluxo de compilação agora utiliza `MidnightOptimizer.spec` com inclusão explícita de todos os módulos (`pros.py`, `game_tweaks.py`, `overlay.py`, `voicefx.py`, `accounts.py`, `oauth_login.py`, `servers.py`, `online.py`) e caminhos dinâmicos `sys._MEIPASS`.
- **Mecanismo de Carregamento Seguro (_safe_import)**: Adicionado fallback dinâmico em `app.py` que pesquisa no diretório executável e em pacotes extraídos, prevenindo qualquer falha por dependência ausente.

### 🔄 Sistema de Atualização Integrado Inteligente (Auto-Restart & Dynamic Banner)
- **Ocultação Automática da Aba de Atualização**: Quando a aplicação já se encontra na versão mais recente, a barra e aba de notificação de atualização desaparecem automaticamente.
- **Deteção Contínua em Segundo Plano**: A aplicação verifica periodicamente novas versões no GitHub a cada 15 minutos; caso uma nova versão seja publicada, a aba volta a surgir de imediato.
- **Reinicio Automático Concluído**: Ao descarregar uma nova versão dentro da app, o processo avisa o utilizador e reinicia automaticamente em 1.5 segundos, aplicando o novo executável de forma transparente.

## [v3.2.0] - 2026-09-24

### 🎯 Miras dos Pros & Viewmodels CS2 (100% Não Destrutivo)
- **Eliminação de Configurações Invasivas**: Remoção total do applier antigo que alterava sensibilidades, resoluções e binds de teclado dos utilizadores.
- **Miras Oficiais com 1 Clique**: Galeria dos melhores pro players mundiais (m0NESY, donk, NiKo, ZywOo, s1mple, ropz, FalleN) com Código de Partilha oficial do CS2 (`CSGO-...`) e comandos diretos para a consola (`~`).
- **Pré-visualização Gráfica da Retícula**: Renderização visual precisa da mira dentro de cada cartão (cor real, gap, espessura, tamanho e ponto central).
- **Posicionamento da Arma (Viewmodels)**: Presets com imagens vetoriais ilustrativas demonstrando exatamente a colocação da arma no ecrã (Clássico Pro, Compacto Recuado, FOV Máximo, Centrado Retro Doom, Padrão Valve e Minimalista).
- **Aplicação Segura e Isolada**: Modos automáticos gravam apenas em ficheiros dedicados (`midnight_crosshair.cfg` e `midnight_viewmodel.cfg`) sem nunca tocar nas tuas binds.

### ⚡ Resolução de Registo de Tiros (Sub-Tick Hitreg Fix)
- **Botão com 1 Clique para Correção de Tiros**: Resolve o desfasamento sub-tick e tiros fantasma que não causam dano no CS2.
- **Limpeza de Cache de Shaders DirectX/GPU**: Esvaziamento automático de ficheiros residuais de shader em NVIDIA DXCache, D3DSCache e AMD DxCache (elimina micro-stutters e quedas de FPS durante tiroteios).
- **Latência Mínima de Rede (Buffer 0 Ticks)**: Configuração de `cl_net_buffer_ticks 0` para eliminar os 15ms-30ms de atraso artificial de interpolação.
- **Taxa Máxima Sub-Tick**: `rate 786432` e alinhamento de frame pacing pós-tick (`engine_low_latency_sleep_after_client_tick true`).
- **Desativação de Throttling Multimédia do Windows**: Prioridade total para pacotes de jogos na pilha de rede.

### 🔔 In-Game Notification Overlay (Popout Animado)
- **Overlay Flutuante dentro do Jogo**: Notificações visuais elegantes que surgem diretamente sobre jogos em ecrã inteiro ou janela borderless.
- **Animação Popout Fluida**: Entrada deslizante e saída suave (popout-in / popout-out) com temporizador decrescente integrado.
- **100% VAC-Safe**: Criado com tecnologia nativa de janelas de sistema (WS_EX_NOACTIVATE e WS_EX_TOOLWINDOW), sem injeção de DLLs, sem ganchos em memória e sem risco de banimento.
- **Sem Perda de Foco**: Não minimiza o CS2 nem rouba cliques do rato durante rondas competitivas.
- **Botão de Teste Integrado**: Testa o aspeto do overlay a qualquer momento na interface.

---

## [v3.1.0] - 2026-09-24

### 🚀 Interface Moderna, Ergonómica e Profissional
- **Novo Design System Obsidian**: Paleta refinada de alta densidade sem exageros visuais, sem neons invasivos e sem efeitos de blur que degradam a legibilidade.
- **Iconografia Vetorial SVG Nativa**: Substituição de símbolos e emojis genéricos por ícones vetoriais modernos e geométricos.
- **Centro de Controlo no Dashboard**: Telemetria em tempo real com leitura precisa de CPU, GPU, RAM e Disco, integrada com dados reais do sistema.
- **Agrupamento de Navegação**: Secções limpas na barra lateral (Geral, Sistema, Ferramentas, Comunidade).
- **Controlos de Janela Integrados**: Minimização, maximização e fecho integrados com a estética Fluent do Windows 11.
- **Consolidação de Folhas de Estilos**: Eliminação de estilos duplicados e transição para o motor CSS unificado `styles.css`.

### ⚡ Desempenho e Estabilidade
- Otimização do agendador de processos e isolamento de prioridade para jogos competitivos.
- Otimização da pilha de rede TCP/IP com rotinas ativas de flush de cache DNS.
- Redução de tempo de carregamento da interface e menor consumo de memória em repouso.

### 📦 Automatização CI/CD e Releases
- Fluxo de trabalho GitHub Actions para Windows (`.github/workflows/release.yml`) que compila automaticamente o executável `MidnightOptimizer.exe` e cria pacotes ZIP a cada nova versão.
- Script de publicação `publicar_versao.ps1` para criação rápida de releases.

---

## [v2.4.5] - 2026-09-20

### 🛡️ Pacote de Otimização Estilo Winhance
- Novas categorias: Privacidade, Debloat, Gaming Extra e Sistema nas Otimizações.
- Diagnóstico do PC com avaliação e recomendações de ajustes.
- Notificações de mensagens no sistema (toast + som + badge).
- Novo tema Call of Duty com tonalidades táticas.
- Melhorias de estabilidade na autenticação e sessões locais.

---

## [v2.3.0] - 2026-09-15

### 🎙️ Estúdio de Voz & Soundboard
- Efeitos de voz com modulação em tempo real.
- Soundboard com suporte para atalhos de teclado configuráveis.
- Suporte para microfone virtual em jogos e Discord.
