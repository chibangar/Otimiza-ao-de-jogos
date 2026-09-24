## 🎯 Midnight Optimizer v3.2.2 — Correção de Executável & Auto-Update Inteligente

### 🛠️ Correções da Versão 3.2.2
- **Correção de Sintaxe (SyntaxError no pros.py)**: Resolvido o erro `SyntaxError: f-string expression part cannot include a backslash` em `pros.py`, garantindo execução impecável sem erros de script.
- **Eliminação do Erro de Inicialização**: Corrigido o erro `ModuleNotFoundError: No module named 'pros'` na versão executável compilada para Windows.
- **Compilação Determinística**: Empacotamento direto através do ficheiro de especificação `MidnightOptimizer.spec` com todos os módulos (`pros.py`, `game_tweaks.py`, `overlay.py`, etc.) incluídos no binário.
- **Aba de Atualização Dinâmica**: A notificação de atualização desaparece automaticamente quando o Midnight Optimizer está na versão mais recente.
- **Reinicio Automático pós-Update**: Ao concluir o download de uma nova versão na app, a aplicação avisa e reinicia automaticamente em 1.5s aplicando o novo executável.
- **Verificação Periódica**: Monitorização contínua a cada 15 minutos; se uma nova versão for publicada no GitHub, a aba reaparece de imediato.

### ✨ Novidades Recentes da Linha v3.2

#### 🎯 Miras dos Pros com 1 Clique (CS2)
- Galeria completa dos melhores pro players do mundo: **m0NESY, donk, NiKo, ZywOo, s1mple, ropz e FalleN**.
- Códigos de Partilha Oficiais do CS2 (`CSGO-...`) para importar diretamente nas Definições do jogo.
- Comandos prontos para a Consola (`~`).
- Pré-visualização gráfica interativa da mira com a cor real, espessura e abertura da retícula.
- **100% Não Destrutivo**: Não altera a sensibilidade do rato, DPI nem resolução do jogador.

#### 🔫 Viewmodels com Imagens Demonstrativas
- 6 presets de posicionamento da arma no ecrã: **Clássico Pro, Compacto Recuado, FOV Máximo, Centrado Retro Doom, Padrão Valve e Minimalista**.
- Imagens vetoriais dentro da app mostrando exatamente onde a arma fica posicionada e o espaço de mira libertado.
- Botão para copiar comandos da consola ou aplicar de forma isolada (`midnight_viewmodel.cfg`).

#### ⚡ Resolução de Registo de Tiros (Sub-Tick Hitreg Fix)
- Botão de 1 clique para resolver desfasamento sub-tick e balas fantasma que não registam no CS2.
- Limpeza automática de caches de shaders DirectX/GPU (elimina micro-stutters e quedas de FPS em duelos).
- Buffer de rede em `0 ticks` (`cl_net_buffer_ticks 0`) para eliminar 15ms-30ms de atraso de interpolação.
- Taxa máxima `rate 786432` e alinhamento de frame pacing (`engine_low_latency_sleep_after_client_tick true`).
- Binds e sensibilidades 100% intactas!

#### 🔔 In-Game Notification Overlay (Popout Animado)
- Notificações transparentes e flutuantes sobre o ecrã do jogo com animação suave de popout de entrada e saída.
- 100% VAC-Safe: Não injeta DLLs nem mexe na memória do CS2.
- Não minimiza o jogo nem perde o foco do rato durante o combate competitivo.


---

### 📋 Requisitos de Sistema
- Windows 10 ou Windows 11 (64-bit)
- Direitos de Administrador para otimizações de energia e registo
