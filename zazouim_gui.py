#!/usr/bin/env python3
# zazouim_gui.py — GUI with "hacker terminal" styling (dark + centered banner)
# Dependencies: pyfiglet, requests, python-whois (optional)
# pip install pyfiglet requests python-whois
# On Debian/Kali: sudo apt install python3-tk

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import tkinter.font as tkfont
import threading
import time
import json
import socket
import platform
import os

try:
    import requests
    from pyfiglet import Figlet
    import whois
except Exception:
    requests = None
    Figlet = None
    whois = None

GITHUB_HANDLE = "KhonsuGod"  # tampil sesuai permintaan

# ------- Helpers (safe public lookups) -------
def safe_ip_lookup(ip):
    res = {"error": "requests not available"}
    if requests is None:
        return res
    try:
        socket.inet_aton(ip)
    except Exception:
        return {"error": "invalid IP"}
    try:
        r = requests.get(f"https://ipinfo.io/{ip}/json", timeout=8)
        if r.ok:
            res = r.json()
        else:
            res = {"error": f"ipinfo status {r.status_code}"}
    except Exception as e:
        res = {"error": str(e)}
    try:
        rev = socket.gethostbyaddr(ip)
        res["reverse_dns"] = rev[0]
    except Exception:
        res.setdefault("reverse_dns", None)
    return res

def safe_github_lookup(username):
    if requests is None:
        return {"error": "requests not available"}
    try:
        r = requests.get(f"https://api.github.com/users/{username}", timeout=8, headers={"User-Agent":"zazouim-gui"})
        if r.status_code == 200:
            return r.json()
        return {"error": f"status {r.status_code}"}
    except Exception as e:
        return {"error": str(e)}

def safe_whois_lookup(domain):
    if whois is None:
        return {"error": "whois module not installed"}
    try:
        w = whois.whois(domain)
        if hasattr(w, "items"):
            return dict(w.items())
        else:
            return {k: v for k, v in w.__dict__.items() if not k.startswith("_")}
    except Exception as e:
        return {"error": str(e)}

# ------- GUI App -------
class ZazouimApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Zazouim — OSINT Deity (THE MOON HAUNTS YOU)")
        self.geometry("980x680")
        self.minsize(760, 480)

        # dark bg
        self.configure(bg="#0b0b0b")

        # state
        self.save_text = tk.BooleanVar(value=False)
        self.save_json = tk.BooleanVar(value=False)
        self.output_dir = "zazouim_out"

        # ttk style (clam allows more styling)
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TButton", padding=6, relief="flat", background="#111111", foreground="#00ff6a")
        style.map("TButton", background=[("active", "#222222")])

        self.create_widgets()
        # after widgets created, print banner with center + typing effect
        self.after(120, lambda: self.print_banner(animate=True))

    def create_widgets(self):
        top = ttk.Frame(self)
        top.pack(fill="x", padx=8, pady=6)

        title_lbl = tk.Label(top, text="ZAZOUIM", font=("Consolas", 20, "bold"), bg="#0b0b0b", fg="#00ff6a")
        title_lbl.pack(side="left", padx=(6,12))

        chk_frame = ttk.Frame(top)
        chk_frame.pack(side="right")
        ttk.Checkbutton(chk_frame, text="Save JSON", variable=self.save_json).pack(side="right", padx=4)
        ttk.Checkbutton(chk_frame, text="Save TXT", variable=self.save_text).pack(side="right", padx=4)

        middle = ttk.Frame(self)
        middle.pack(fill="both", expand=True, padx=8, pady=6)

        left = ttk.Frame(middle, width=260)
        left.pack(side="left", fill="y", padx=(0,8))

        art_btn = ttk.Button(left, text="Refresh Banner", command=lambda: self.print_banner(animate=True))
        art_btn.pack(fill="x", pady=(0,6))

        ttk.Label(left, text="Input (arg):", background="#0b0b0b", foreground="#00ff6a").pack(anchor="w")
        self.input_var = tk.StringVar()
        entry = ttk.Entry(left, textvariable=self.input_var)
        entry.pack(fill="x", pady=(0,8))

        ttk.Button(left, text="List (help)", command=self.cmd_list).pack(fill="x", pady=3)
        ttk.Button(left, text="Doxing (THE MOON HAUNTS YOU)", command=self.cmd_doxing).pack(fill="x", pady=3)
        ttk.Button(left, text="IP Lookup", command=self.cmd_ip).pack(fill="x", pady=3)
        ttk.Button(left, text="WHOIS", command=self.cmd_whois).pack(fill="x", pady=3)
        ttk.Button(left, text="GitHub Profile", command=self.cmd_github).pack(fill="x", pady=3)

        ttk.Button(left, text="Open Output Folder", command=self.open_output_dir).pack(fill="x", pady=(20,3))
        ttk.Button(left, text="Export Last Text...", command=self.save_last_json_dialog).pack(fill="x", pady=3)

        right = ttk.Frame(middle)
        right.pack(side="right", fill="both", expand=True)

        # monospaced green-on-black console
        con_font = tkfont.Font(family="Consolas", size=11)
        self.text = scrolledtext.ScrolledText(right, wrap="word", font=con_font, bg="#0b0b0b", fg="#00ff6a",
                                              insertbackground="#00ff6a", padx=8, pady=8, borderwidth=0)
        self.text.pack(fill="both", expand=True)
        self.text.configure(state="disabled")

        # configure tags for colors/center
        self.text.tag_configure("center", justify="center")
        self.text.tag_configure("dim", foreground="#6b6b6b")
        self.text.tag_configure("warning", foreground="#ff6a6a", font=("Consolas", 11, "bold"))

        status = ttk.Frame(self)
        status.pack(fill="x", padx=8, pady=(0,8))
        self.status_var = tk.StringVar(value="Ready")
        lbl_status = tk.Label(status, textvariable=self.status_var, bg="#0b0b0b", fg="#00ff6a")
        lbl_status.pack(side="left")

    # ---------- output helpers ----------
    def write(self, s, newline=True, tag=None):
        self.text.configure(state="normal")
        if newline:
            self.text.insert("end", s + "\n")
            if tag:
                # tag last inserted line
                start_index = "end-1l linestart"
                end_index = "end-1l lineend"
                self.text.tag_add(tag, start_index, end_index)
        else:
            self.text.insert("end", s)
        self.text.see("end")
        self.text.configure(state="disabled")

    def clear_output(self):
        self.text.configure(state="normal")
        self.text.delete("1.0", "end")
        self.text.configure(state="disabled")

    def set_status(self, s):
        self.status_var.set(s)
        self.update_idletasks()

    # ---------- banner (center + typing) ----------
    def print_banner(self, animate=False):
        # produce banner text (figlet if available)
        banner = ""
        if Figlet is not None:
            try:
                f = Figlet(font="slant")
                banner = f.renderText("ZAZOUIM")
            except Exception:
                banner = "ZAZOUIM\n"
        else:
            banner = "ZAZOUIM\n"

        # Prepare demo header and lines
        header_lines = [
            banner.rstrip("\n"),
            "By the moon’s command, I have wandered through shadow and sin. The marked one has been found, and their silence now belongs to you, Khonsu.",
            "",
            "Mau Akses? HELL nahh ini gua bikin buat edukasi aja guys xixixixi",
            ""
        ]
        self.clear_output()
        # typing effect: print line by line centered
        for line in header_lines:
            self._insert_centered_line(line)
            if animate:
                time.sleep(0.05)
                self.update()
        # also print small separator
        self._insert_centered_line("─" * 60, tag="dim")

    def _insert_centered_line(self, text_line, tag=None):
        # Insert a line and center it using tag 'center'
        self.text.configure(state="normal")
        self.text.insert("end", text_line + "\n")
        last_start = "end-1l linestart"
        last_end = "end-1l lineend"
        self.text.tag_add("center", last_start, last_end)
        if tag:
            self.text.tag_add(tag, last_start, last_end)
        self.text.see("end")
        self.text.configure(state="disabled")

    # ---------- operations ----------
    def cmd_list(self):
        txt = (
            "Allowed commands (buttons):\n"
            "- List (this help)\n"
            "- Doxing (THE MOON HAUNTS YOU) -> shows\n"
            "- IP Lookup -> enter IP in input box\n"
            "- WHOIS -> enter domain in input box\n"
            "- GitHub Profile -> enter username in input box\n\n"
            "Toggle Save TXT/JSON to store outputs in ./zazouim_out\n"
        )
        self.write(txt)

    def cmd_doxing(self):
        demo = (
            "────────────────────────────────────────────────────────────\n"
            "By the moon’s command, I have wandered through shadow and sin\n"
            "Tunduklah di bawah cahaya rembulan.\n"
            "────────────────────────────────────────────────────────────\n\n"
            f"Run by (GitHub)      : {GITHUB_HANDLE}\n\n"
            "PROVINSI              : DKI JAKARTA | JAKARTA SELATAN \n"
            "NIK                   : 3671-0725-0604-0004 \n"
            "Nama                  : MUHAMMAD RIDHO ADITYA \n"
            "Tempat/Tgl lahir      : JAKARTA, 25-06-2004 \n"
            "Jenis Kelamin         : LAKI-LAKI \n"
            "RT/RW                 : 004/004 \n"
            "Kel/Desa              : PETUKANGAN UTARA\n"
            "Kecamatan             : PESANGGRAHAN \n"
            "Agama                 : ISLAM \n"
            "Status Perkawinan     : BELUM KAWIN\n"
            "Pekerjaan             : PELAJAR/MAHASISWA\n"
            "Kewarganegaraan       : WNI\n"
            "Berlaku Hingga        : SEUMUR HIDUP\n\n"
            "────────────────────────────────────────────────────────────\n"
            "THX ZAZOUIM — buat insight soal exploit & tools. Khonsu was here\n"
            "For ethical use only. Jangan disalahgunakan. Zazouim dan Khonsu menyaksikan.\n"
            "────────────────────────────────────────────────────────────\n"
        )
        # write lines and center them for terminal look
        for line in demo.splitlines():
            self._insert_centered_line(line)
        self.set_status("Displayed doxing by zazouim.")

    def _run_in_thread(self, fn, *args):
        t = threading.Thread(target=fn, args=args, daemon=True)
        t.start()

    def cmd_ip(self):
        arg = self.input_var.get().strip()
        if not arg:
            messagebox.showinfo("Input needed", "Masukkan IP di kotak 'Input (arg)'.")
            return
        self.set_status("Querying IP...")
        self._run_in_thread(self._do_ip, arg)

    def _do_ip(self, ip):
        res = safe_ip_lookup(ip)
        self.write(f"IP Lookup -> {ip}")
        self.write(json.dumps(res, indent=2, ensure_ascii=False))
        if self.save_text.get():
            self._save_file(f"{ip}_ip.txt", json.dumps(res, indent=2, ensure_ascii=False))
        if self.save_json.get():
            self._save_file(f"{ip}_ip.json", json.dumps(res, indent=2, ensure_ascii=False))
        self.set_status("IP query finished.")

    def cmd_github(self):
        arg = self.input_var.get().strip()
        if not arg:
            messagebox.showinfo("Input needed", "Masukkan GitHub username di kotak 'Input (arg)'.")
            return
        self.set_status("Querying GitHub...")
        self._run_in_thread(self._do_github, arg)

    def _do_github(self, username):
        res = safe_github_lookup(username)
        self.write(f"GitHub -> {username}")
        self.write(json.dumps(res, indent=2, ensure_ascii=False))
        if self.save_text.get():
            self._save_file(f"{username}_github.txt", json.dumps(res, indent=2, ensure_ascii=False))
        if self.save_json.get():
            self._save_file(f"{username}_github.json", json.dumps(res, indent=2, ensure_ascii=False))
        self.set_status("GitHub query finished.")

    def cmd_whois(self):
        arg = self.input_var.get().strip()
        if not arg:
            messagebox.showinfo("Input needed", "Masukkan domain di kotak 'Input (arg)'.")
            return
        self.set_status("Querying WHOIS...")
        self._run_in_thread(self._do_whois, arg)

    def _do_whois(self, domain):
        res = safe_whois_lookup(domain)
        self.write(f"WHOIS -> {domain}")
        try:
            self.write(json.dumps(res, indent=2, default=str, ensure_ascii=False))
            if self.save_text.get():
                self._save_file(f"{domain}_whois.txt", json.dumps(res, indent=2, default=str, ensure_ascii=False))
            if self.save_json.get():
                self._save_file(f"{domain}_whois.json", json.dumps(res, indent=2, default=str, ensure_ascii=False))
        except Exception as e:
            self.write(f"WHOIS error: {e}")
        self.set_status("WHOIS query finished.")

    def _save_file(self, name, content):
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir, exist_ok=True)
        path = os.path.join(self.output_dir, name)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        self.write(f"[Saved] {path}")

    def open_output_dir(self):
        p = self.output_dir
        if not os.path.exists(p):
            os.makedirs(p, exist_ok=True)
        if platform.system() == "Windows":
            os.startfile(p)
        elif platform.system() == "Darwin":
            os.system(f"open {p}")
        else:
            os.system(f"xdg-open {p}")

    def save_last_json_dialog(self):
        content = self.text.get("1.0", "end").strip()
        if not content:
            messagebox.showinfo("No content", "Output kosong.")
            return
        f = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text","*.txt"),("All","*.*")])
        if f:
            with open(f, "w", encoding="utf-8") as fh:
                fh.write(content)
            messagebox.showinfo("Saved", f"Tersimpan ke {f}")

# ---------------- run app ----------------
def main():
    app = ZazouimApp()
    app.mainloop()

if __name__ == "__main__":
    main()
