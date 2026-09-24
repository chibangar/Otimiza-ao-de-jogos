"""
Midnight Optimizer — In-Game Notification Overlay
Overlay não intrusivo, borderless, transparente e topmost.
100% VAC-Safe: Não injeta DLLs nem mexe na memória do CS2/jogos.
Usa Win32 WS_EX_NOACTIVATE para nunca tirar o foco nem minimizar o jogo.
"""
import sys
import os
import time
import threading
import subprocess
import tkinter as tk

GWL_EXSTYLE = -20
WS_EX_NOACTIVATE = 0x08000000
WS_EX_TOOLWINDOW = 0x00000080
WS_EX_TOPMOST = 0x00000008
WS_EX_LAYERED = 0x00080000

def _apply_win32_styles(root):
    try:
        import ctypes
        user32 = ctypes.windll.user32
        root.update_idletasks()
        hwnd = user32.GetParent(root.winfo_id()) or root.winfo_id()
        cur = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        user32.SetWindowLongW(hwnd, GWL_EXSTYLE, cur | WS_EX_NOACTIVATE | WS_EX_TOOLWINDOW)
    except Exception:
        pass


def show_in_game_overlay(title="Midnight Optimizer", message="Otimização aplicada com sucesso!",
                        badge="CS2 SUB-TICK", theme="emerald", duration_sec=3.8):
    """
    Cria uma janela overlay flutuante com animação de popout (aparece e desaparece).
    Totalmente isolada, auto-destrutiva após o tempo configurado.
    """
    try:
        root = tk.Tk()
    except Exception as e:
        print(f"[Overlay] Erro ao iniciar Tk: {e}")
        return

    root.overrideredirect(True)
    root.attributes("-topmost", True)

    # Configuração de cores
    themes = {
        "emerald": {"accent": "#10b981", "bg": "#0c0e14", "border": "#1e293b", "badge_bg": "#064e3b", "badge_fg": "#34d399"},
        "gold": {"accent": "#f59e0b", "bg": "#0c0e14", "border": "#2d2415", "badge_bg": "#451a03", "badge_fg": "#fbbf24"},
        "cyan": {"accent": "#06b6d4", "bg": "#0c0e14", "border": "#164e63", "badge_bg": "#083344", "badge_fg": "#22d3ee"},
        "purple": {"accent": "#8b5cf6", "bg": "#0c0e14", "border": "#2e1065", "badge_bg": "#2e1065", "badge_fg": "#c084fc"},
    }
    th = themes.get(theme, themes["emerald"])

    w, h = 370, 78
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()

    target_x = sw - w - 24
    target_y = 26
    start_x = sw + 20  # começa fora do ecrã à direita para efeito de popout

    root.geometry(f"{w}x{h}+{start_x}+{target_y}")
    root.configure(bg=th["bg"])

    # Canvas para desenho do cartão e barra de progresso
    cv = tk.Canvas(root, width=w, height=h, bg=th["bg"], highlightthickness=1, highlightbackground=th["border"])
    cv.pack(fill="both", expand=True)

    # Faixa lateral de destaque (accent line)
    cv.create_rectangle(0, 0, 5, h, fill=th["accent"], width=0)

    # Badge no canto superior direito
    badge_text = badge.upper()
    cv.create_text(w - 18, 18, text=badge_text, fill=th["badge_fg"],
                   font=("Segoe UI", 8, "bold"), anchor="e")

    # Ícone / Marcador visual
    cv.create_oval(18, 14, 26, 22, fill=th["accent"], outline="")

    # Título
    cv.create_text(34, 18, text=title[:38], fill="#ffffff",
                   font=("Segoe UI", 10, "bold"), anchor="w")

    # Mensagem de detalhe
    msg_wrapped = message
    if len(msg_wrapped) > 85:
        msg_wrapped = msg_wrapped[:82] + "..."
    cv.create_text(18, 44, text=msg_wrapped, fill="#94a3b8",
                   font=("Segoe UI", 8), anchor="w")

    # Linha de progresso sutil na base
    bar_id = cv.create_rectangle(0, h - 3, w, h, fill=th["accent"], width=0)

    _apply_win32_styles(root)

    # --- Animação de Entrada (Popout In) ---
    frames_in = 14
    dx = (target_x - start_x) / frames_in
    cur_x = float(start_x)

    def animate_in(step=0):
        nonlocal cur_x
        if step < frames_in:
            cur_x += dx
            root.geometry(f"{w}x{h}+{int(cur_x)}+{target_y}")
            root.after(12, lambda: animate_in(step + 1))
        else:
            root.geometry(f"{w}x{h}+{target_x}+{target_y}")
            # Iniciar contagem decrescente da barra de progresso
            start_hold()

    # --- Contagem de exibição e progresso ---
    total_steps = 40
    step_delay = int((duration_sec * 1000) / total_steps)

    def start_hold():
        def update_bar(cur_step=0):
            if cur_step <= total_steps:
                pct = 1.0 - (cur_step / total_steps)
                cv.coords(bar_id, 0, h - 3, int(w * pct), h)
                root.after(step_delay, lambda: update_bar(cur_step + 1))
            else:
                animate_out()
        update_bar(0)

    # --- Animação de Saída (Popout Out) ---
    frames_out = 12
    out_dx = (sw + 30 - target_x) / frames_out
    exit_x = float(target_x)

    def animate_out(step=0):
        nonlocal exit_x
        if step < frames_out:
            exit_x += out_dx
            root.geometry(f"{w}x{h}+{int(exit_x)}+{target_y}")
            root.after(12, lambda: animate_out(step + 1))
        else:
            try:
                root.destroy()
            except Exception:
                pass

    root.after(10, animate_in)
    try:
        root.mainloop()
    except Exception:
        pass


def notify_async(title="Midnight Optimizer", message="Otimização aplicada!",
                 badge="CS2 SUB-TICK", theme="emerald", duration_sec=3.8):
    """Dispara a notificação de overlay sem bloquear a thread principal."""
    # Se estivermos num subprocesso isolado ou thread:
    t = threading.Thread(
        target=show_in_game_overlay,
        args=(title, message, badge, theme, duration_sec),
        daemon=True
    )
    t.start()


def notify_process(title="Midnight Optimizer", message="Otimização aplicada!",
                   badge="CS2 SUB-TICK", theme="emerald", duration_sec=3.8):
    """
    Dispara o overlay através de um subprocesso leve para isolamento absoluto de memória/GUI.
    Garante que não há conflito com o loop de eventos do WebView2.
    """
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        if getattr(sys, "frozen", False):
            cmd = [
                sys.executable,
                "--overlay",
                "--title", str(title),
                "--msg", str(message),
                "--badge", str(badge),
                "--theme", str(theme),
                "--duration", str(duration_sec)
            ]
        else:
            cmd = [
                sys.executable,
                os.path.join(base_dir, "overlay.py"),
                "--title", str(title),
                "--msg", str(message),
                "--badge", str(badge),
                "--theme", str(theme),
                "--duration", str(duration_sec)
            ]
        kw = {"creationflags": getattr(subprocess, "CREATE_NO_WINDOW", 0)}
        subprocess.Popen(cmd, **kw)
    except Exception:
        # Fallback para thread direta
        notify_async(title, message, badge, theme, duration_sec)


def handle_cli(args):
    """Trata argumentos passados pela linha de comando."""
    title = "Midnight Optimizer"
    message = "Notificação de Overlay In-Game"
    badge = "CS2"
    theme = "emerald"
    duration = 3.8

    i = 0
    while i < len(args):
        a = args[i]
        if a == "--title" and i + 1 < len(args):
            title = args[i + 1]
            i += 2
        elif a == "--msg" and i + 1 < len(args):
            message = args[i + 1]
            i += 2
        elif a == "--badge" and i + 1 < len(args):
            badge = args[i + 1]
            i += 2
        elif a == "--theme" and i + 1 < len(args):
            theme = args[i + 1]
            i += 2
        elif a == "--duration" and i + 1 < len(args):
            try:
                duration = float(args[i + 1])
            except ValueError:
                pass
            i += 2
        else:
            i += 1

    show_in_game_overlay(title, message, badge, theme, duration)


if __name__ == "__main__":
    handle_cli(sys.argv[1:])
