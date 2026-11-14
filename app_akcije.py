"""
Yahoo Finance stil aplikacija za pregled akcija.

Pokretanje:
    python app_akcije.py
"""

import tkinter as tk
from tkinter import ttk, messagebox

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.dates as mdates

import yfinance as yf

# Tamna tema (Yahoo Finance stil)
BG = "#131722"
PANEL = "#1e222d"
FG = "#d1d4dc"
ACCENT = "#2962ff"
GREEN = "#0ecb81"
RED = "#f6465d"
MUTED = "#5d606b"

PERIODS = {"1M": "1mo", "3M": "3mo", "6M": "6mo", "1Y": "1y", "5Y": "5y", "MAX": "max"}


class AkcijeApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Yahoo Finance - Pregled akcija")
        self.geometry("1100x750")
        self.configure(bg=BG)

        self.ticker = tk.StringVar()
        self.current_period = tk.StringVar(value="1Y")
        self.data = None
        self.info = {}

        self._build_ui()
        self.protocol("WM_DELETE_WINDOW", self.destroy)

    # ---------- UI ----------
    def _build_ui(self):
        # Gornja traka
        top = tk.Frame(self, bg=PANEL, pady=10)
        top.pack(fill="x")

        tk.Label(top, text="Ticker:", bg=PANEL, fg=FG,
                 font=("Segoe UI", 11)).pack(side="left", padx=(15, 5))
        entry = tk.Entry(top, textvariable=self.ticker, bg="#2a2e39", fg=FG,
                         insertbackground=FG, relief="flat", font=("Segoe UI", 12),
                         width=10)
        entry.pack(side="left", ipady=5)
        entry.bind("<Return>", lambda e: self.ucitaj())

        tk.Button(top, text="Učitaj", command=self.ucitaj, bg=ACCENT, fg="white",
                  relief="flat", font=("Segoe UI", 10, "bold"), padx=15,
                  cursor="hand2").pack(side="left", padx=10)

        # Periodi
        per_frame = tk.Frame(top, bg=PANEL)
        per_frame.pack(side="right", padx=15)
        for label in PERIODS:
            rb = tk.Radiobutton(per_frame, text=label, variable=self.current_period,
                                value=label, bg=PANEL, fg=MUTED, selectcolor=PANEL,
                                activebackground=PANEL, activeforeground=FG,
                                font=("Segoe UI", 9), command=self.osvjezi_grafik,
                                cursor="hand2")
            rb.pack(side="left", padx=3)

        # Sadržaj
        main = tk.Frame(self, bg=BG)
        main.pack(fill="both", expand=True, padx=15, pady=10)

        # Lijevi panel - statistike
        left = tk.Frame(main, bg=PANEL, width=280)
        left.pack(side="left", fill="y", padx=(0, 10))
        left.pack_propagate(False)

        self.stats_frame = tk.Frame(left, bg=PANEL)
        self.stats_frame.pack(fill="both", expand=True, padx=15, pady=15)

        self.stats_placeholder = tk.Label(
            self.stats_frame, text="Unesi ticker i klikni 'Učitaj'",
            bg=PANEL, fg=MUTED, font=("Segoe UI", 11), wraplength=240)
        self.stats_placeholder.pack(expand=True)

        # Desni panel - grafikon
        right = tk.Frame(main, bg=BG)
        right.pack(side="left", fill="both", expand=True)

        self.fig = Figure(figsize=(8, 6), dpi=100, facecolor=BG)
        self.ax_price = self.fig.add_subplot(211)
        self.ax_vol = self.fig.add_subplot(212, sharex=self.ax_price)
        self.canvas = FigureCanvasTkAgg(self.fig, master=right)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        self._stilizuj_prazan_grafik()

    def _stilizuj_prazan_grafik(self):
        for ax in (self.ax_price, self.ax_vol):
            ax.set_facecolor(PANEL)
            ax.tick_params(colors=MUTED, labelsize=8)
            for spine in ax.spines.values():
                spine.set_color("#2a2e39")
        self.ax_price.text(0.5, 0.5, "Nema podataka", transform=self.ax_price.transAxes,
                           ha="center", va="center", color=MUTED, fontsize=14)
        self.ax_vol.set_visible(False)
        self.fig.tight_layout()
        self.canvas.draw()

    # ---------- Logika ----------
    def ucitaj(self):
        tiker = self.ticker.get().strip().upper()
        if not tiker:
            return
        try:
            self.data = yf.Ticker(tiker)
            self.info = self.data.info
            if not self.info or self.info.get("regularMarketPrice") is None:
                raise ValueError("Ticker nije pronađen")
            self.prikazi_statistike()
            self.osvjezi_grafik()
        except Exception as e:
            messagebox.showerror("Greška", f"Nije moguće učitati '{tiker}':\n{e}")

    def osvjezi_grafik(self):
        if self.data is None:
            return
        period = PERIODS[self.current_period.get()]
        try:
            hist = self.data.history(period=period, auto_adjust=True)
        except Exception as e:
            messagebox.showerror("Greška", f"Greška pri učitavanju istorije: {e}")
            return
        if hist.empty:
            return
        self._crtaj_grafik(hist)

    def _crtaj_grafik(self, hist):
        self.ax_price.clear()
        self.ax_vol.clear()
        self.ax_vol.set_visible(True)

        close = hist["Close"]
        volume = hist["Volume"]
        dates = hist.index

        # Cijena
        self.ax_price.plot(dates, close, color=ACCENT, linewidth=1.8)
        self.ax_price.fill_between(dates, close, alpha=0.08, color=ACCENT)

        # Prosjek (puna linija) - Yahoo stil
        ma = close.rolling(window=50).mean()
        self.ax_price.plot(dates, ma, color="#ff9800", linewidth=1, alpha=0.8)

        # Promjena u periodu
        promjena = (close.iloc[-1] - close.iloc[0]) / close.iloc[0] * 100
        self.ax_price.set_title(
            f"{self.ticker.get().upper()}  {close.iloc[-1]:.2f}  "
            f"({promjena:+.2f}%)",
            loc="left", color=FG, fontsize=14, fontweight="bold", pad=10)

        # Formatiranje
        self.ax_price.tick_params(colors=MUTED, labelsize=8)
        self.ax_price.yaxis.set_major_formatter(
            plt.FuncFormatter(lambda x, p: f"{x:,.2f}"))
        self.ax_price.grid(color="#2a2e39", linewidth=0.5, alpha=0.6)

        # Datum na x-osi
        self.ax_price.xaxis.set_major_formatter(mdates.DateFormatter("%b %y"))
        self.ax_price.xaxis.set_major_locator(mdates.AutoDateLocator())
        plt.setp(self.ax_price.xaxis.get_majorticklabels(), rotation=45, ha="right")

        # Volumen
        colors = [GREEN if c >= o else RED for c, o in zip(close, hist["Open"])]
        self.ax_vol.bar(dates, volume, color=colors, width=0.8, alpha=0.7)
        self.ax_vol.tick_params(colors=MUTED, labelsize=8)
        self.ax_vol.yaxis.set_major_formatter(
            plt.FuncFormatter(lambda x, p: f"{x/1e6:.1f}M" if x >= 1e6 else f"{x/1e3:.0f}K"))
        self.ax_vol.grid(color="#2a2e39", linewidth=0.5, alpha=0.6)
        self.ax_vol.set_ylabel("Volumen", color=MUTED, fontsize=8)

        for ax in (self.ax_price, self.ax_vol):
            ax.set_facecolor(PANEL)
            for spine in ax.spines.values():
                spine.set_color("#2a2e39")

        self.fig.tight_layout()
        self.canvas.draw()

    def prikazi_statistike(self):
        for w in self.stats_frame.winfo_children():
            w.destroy()

        i = self.info
        tiker = self.ticker.get().upper()

        # Header
        tk.Label(self.stats_frame, text=tiker, bg=PANEL, fg=FG,
                 font=("Segoe UI", 18, "bold")).pack(anchor="w")
        tk.Label(self.stats_frame, text=i.get("shortName", ""), bg=PANEL, fg=MUTED,
                 font=("Segoe UI", 10)).pack(anchor="w", pady=(0, 10))

        # Trenutna cijena
        cijena = i.get("currentPrice") or i.get("regularMarketPrice")
        if cijena:
            tk.Label(self.stats_frame, text=f"{cijena:,.2f} {i.get('currency', '')}",
                     bg=PANEL, fg=FG, font=("Segoe UI", 22, "bold")).pack(anchor="w")

        # Lista statistika
        stavke = [
            ("Prethodno zatvaranje", i.get("previousClose")),
            ("Otvaranje", i.get("open")),
            ("Dan max", i.get("dayHigh")),
            ("Dan min", i.get("dayLow")),
            ("52-ned max", i.get("fiftyTwoWeekHigh")),
            ("52-ned min", i.get("fiftyTwoWeekLow")),
            ("Tržišna kapitalizacija", self._fmt(i.get("marketCap"))),
            ("P/E odnos", self._fmt(i.get("trailingPE"))),
            ("EPS", self._fmt(i.get("trailingEps"))),
            ("Dividendna stopa", self._fmt_proc(i.get("dividendYield"))),
            ("Beta", self._fmt(i.get("beta"))),
            ("Sektor", i.get("sector")),
            ("Industrija", i.get("industry")),
            ("Zemlja", i.get("country")),
            ("Valuta", i.get("currency")),
            ("Prosečan volumen", self._fmt(i.get("averageVolume"))),
        ]

        for naziv, vrijednost in stavke:
            if vrijednost is None:
                continue
            row = tk.Frame(self.stats_frame, bg=PANEL)
            row.pack(fill="x", pady=2)
            tk.Label(row, text=naziv, bg=PANEL, fg=MUTED,
                     font=("Segoe UI", 9), anchor="w").pack(side="left")
            tk.Label(row, text=str(vrijednost), bg=PANEL, fg=FG,
                     font=("Segoe UI", 9, "bold"), anchor="e").pack(side="right")

    @staticmethod
    def _fmt(v):
        if v is None:
            return None
        if isinstance(v, float):
            return f"{v:,.2f}"
        return f"{v:,}"

    @staticmethod
    def _fmt_proc(v):
        if v is None:
            return None
        return f"{v * 100:.2f}%"


if __name__ == "__main__":
    app = AkcijeApp()
    app.mainloop()
