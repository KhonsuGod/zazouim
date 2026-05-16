#!/usr/bin/env python3
# zazouim.py — safe demo CLI (REPL + fake doxing demo)
# Dependencies: rich, pyfiglet
# pip install rich pyfiglet

from rich.console import Console
from rich.panel import Panel
from pyfiglet import Figlet
import time
import sys

console = Console()

def banner():
    f = Figlet(font="slant")
    console.print(f.renderText("ZAZOUIM"), style="cyan")
    console.print("[yellow]The Eye of Khonsu Awakens...[/yellow]\n")

def ritual_loading(text="Invoking lunar energies...", delay=0.01):
    for c in text:
        console.print(c, end="", highlight=False)
        time.sleep(delay)
    console.print()

# ---------- safe / sanitized fake demo ----------
def cmd_doxing(_=None):
    """
    FAKE DEMO — menampilkan contoh fiktif untuk edukasi/UI.
    Menampilkan GitHub handle (KhonsuGod). Semua field lain clearly labeled DEMO.
    """
    github = "KhonsuGod"  # tampilkan GitHub handle sesuai permintaan

    demo_text = f"""────────────────────────────────────────────────────────────
By the moon’s command, I have wandered through shadow and sin.
This output is a FAKE DEMO for education only — do not use for real doxxing.
────────────────────────────────────────────────────────────

Run by (GitHub)      : {github}

PROVINSI              : DKI JAKARTA | JAKARTA SELATAN (DEMO)
NIK                   : DEMO-3671-0725-0604-000X (DEMO)
Nama                  : NAMA CONTOH (DEMO)
Tempat/Tgl lahir      : JAKARTA, 25-06-2004 (DEMO)
Jenis Kelamin         : LAKI-LAKI (DEMO)
RT/RW                 : 004/004 (DEMO)
Kel/Desa              : PETUKANGAN UTARA (DEMO)
Kecamatan             : PESANGGRAHAN (DEMO)
Agama                 : ISLAM (DEMO)
Status Perkawinan     : BELUM KAWIN (DEMO)
Pekerjaan             : PELAJAR/MAHASISWA (DEMO)
Kewarganegaraan       : WNI (DEMO)
Berlaku Hingga        : SEUMUR HIDUP (DEMO)

────────────────────────────────────────────────────────────
PENTING: Ini output DEMO/FIKTIF untuk tujuan edukasi saja.
Jangan gunakan command ini untuk mencari, mengumpulkan, atau menyebarkan data pribadi nyata.
Gunakan API resmi dan minta izin jika butuh data nyata untuk riset.
────────────────────────────────────────────────────────────
"""

    console.print(Panel.fit(
        demo_text,
        title="[magenta]DOXING — DEMO (FAKE)[/magenta]",
        subtitle="EDUCATION ONLY — Zazouim • Khonsu power (respect it)",
        subtitle_align="right"
    ))

# ---------- simple REPL commands ----------
def cmd_list(_=None):
    console.print("[cyan]Available commands (legal + demos):[/cyan]")
    console.print("- list        : show this help")
    console.print("- doxing      : demo (FAKE) — education only")
    console.print("- exit/quit   : exit the program")
    console.print("\nTip: Use this CLI for learning and UI demo only.\n")

def parse_and_run(line):
    if not line:
        return
    parts = line.strip().split()
    cmd = parts[0].lower()
    if cmd in ("list", "help"):
        cmd_list()
    elif cmd == "doxing":
        cmd_doxing()
    elif cmd in ("exit", "quit"):
        console.print("[magenta]Farewell.[/magenta]")
        sys.exit(0)
    else:
        console.print("[red]Unknown command.[/red] Type 'list'.")

def main():
    banner()
    ritual_loading()
    console.print("[dim]Type 'list' to see allowed commands. Placeholders for demo only.[/dim]\n")
    while True:
        try:
            line = console.input("[bold cyan]zazouim> [/bold cyan]")
            parse_and_run(line)
        except KeyboardInterrupt:
            console.print("\n[red]Interrupted. Type 'exit' to quit.[/red]")
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")

if __name__ == "__main__":
    main()
