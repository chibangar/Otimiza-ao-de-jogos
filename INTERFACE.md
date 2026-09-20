# Midnight — nova interface Ion

A interface foi redesenhada em todas as 11 áreas da app. Inclui um novo login,
navegação por grupos, dashboard, quatro atmosferas (Ion, Void, Solar e Ops),
reator orbital animado, partículas, luz reativa ao rato e transições.

O botão de brilho na barra superior reduz os efeitos e guarda a preferência.
As animações respeitam a preferência de movimento reduzido do sistema.
As partículas e as animações contínuas param quando a janela fica oculta.

## Abrir

- **App Windows:** executar `iniciar.bat`, com Python e as dependências de
  `requirements.txt` instalados. A interface utiliza a ligação pywebview existente.
- **Pré-visualização:** `npm run preview`, depois abrir
  <http://127.0.0.1:4173/?preview=1> e escolher **Explorar a nova interface**.
- **Verificação de sintaxe:** `npm run check`.
- **Compilar EXE:** `build_exe.bat`. A lista de recursos do PyInstaller inclui
  `interface.css` e `interface.js`.

A pré-visualização permite explorar páginas, pesquisa e temas. Não estabelece
sessão numa conta nem executa otimizações Windows. Ações nativas apresentam uma
mensagem explicativa e as métricas sem ligação ficam sem valores. A telemetria de
FPS continua identificada como indisponível, como na app original.

## Ficheiros

- `index.html`: estrutura, login, navegação e dashboard.
- `interface.css`: identidade visual, componentes, animações e layout responsivo.
- `interface.js`: ícones, efeitos, movimento reduzido e acessibilidade dos diálogos.
- `renderer.js`: integra a nova apresentação, mantém os comandos nativos existentes,
  inicializa a navegação antes da descoberta de hardware e suporta a pré-visualização.
- `styles.css`: estilos de base dos componentes existentes.

Os anteriores `redesign.css` e `styles-modern.css` permanecem na pasta, mas já não
são carregados. Não há bibliotecas de animação novas nem dependências npm novas.

## Verificação efetuada

- Sintaxe dos scripts JavaScript.
- Navegação das 11 páginas a 1280 × 800 e 390 × 844, sem excesso horizontal.
- Dashboard à dimensão mínima da app: 1024 × 640.
- Pesquisa com teclado, quatro temas, redução de movimento e retorno ao login.
- Bloqueio de ações Windows na pré-visualização.

As operações reais do sistema e a compilação do executável não foram executadas
neste ambiente. A pasta de trabalho é uma cópia sem `.git`; as alterações são locais.
