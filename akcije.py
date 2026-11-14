"""
Program za povlačenje podataka o akcijama sa Yahoo Finance-a.

Pokretanje:
    python akcije.py

Potrebna biblioteka:
    pip install yfinance pandas
"""

import yfinance as yf
import pandas as pd


def povuci_podatke(tiker: str) -> None:
    """Povlači i ispisuje sve dostupne podatke o akciji za dati tiker."""
    print(f"\nPovlačim podatke za {tiker} ...\n")

    akcija = yf.Ticker(tiker)

    # Osnovni podaci o akciji
    info = akcija.info
    print("=" * 60)
    print(f"  AKCIJA: {info.get('shortName', tiker)} ({tiker})")
    print("=" * 60)

    polja = [
        ("Trenutna cena", "currentPrice"),
        ("Prethodno zatvaranje", "previousClose"),
        ("Otvaranje", "open"),
        ("Najviša cena dana", "dayHigh"),
        ("Najniža cena dana", "dayLow"),
        ("Pedesetdvanaestonedeljni maksimum", "fiftyTwoWeekHigh"),
        ("Pedesetdvanaestonedeljni minimum", "fiftyTwoWeekLow"),
        ("Tržišna kapitalizacija", "marketCap"),
        ("P/E odnos", "trailingPE"),
        ("EPS", "trailingEps"),
        ("Dividendna stopa", "dividendYield"),
        ("Beta", "beta"),
        ("Sektor", "sector"),
        ("Industrija", "industry"),
        ("Zemlja", "country"),
        ("Valuta", "currency"),
        ("Prosečan volumen", "averageVolume"),
        ("52-nedeljna promena", "52WeekChange"),
    ]

    for naziv, kljuc in polja:
        vrednost = info.get(kljuc)
        if vrednost is not None:
            if kljuc == "marketCap":
                vrednost = f"{vrednost:,.0f}"
            elif kljuc == "dividendYield":
                vrednost = f"{vrednost * 100:.2f}%"
            elif kljuc == "52WeekChange":
                vrednost = f"{vrednost * 100:.2f}%"
            print(f"  {naziv:<35}: {vrednost}")

    # Istorijske cene (zadnjih 30 dana)
    print("\n" + "=" * 60)
    print("  ISTORIJSKE CENE (zadnjih 30 dana)")
    print("=" * 60)

    istorija = akcija.history(period="1mo")
    if istorija.empty:
        print("  Nema dostupnih istorijskih podataka.")
    else:
        istorija = istorija[["Open", "High", "Low", "Close", "Volume"]]
        istorija.columns = ["Otvaranje", "Najvis", "Najnis", "Zatvaranje", "Volumen"]
        istorija = istorija.round(2)
        print(istorija.tail(10).to_string())

    # Finansijski izvještaji
    print("\n" + "=" * 60)
    print("  FINANSIJSKI IZVJEŠTAJI")
    print("=" * 60)

    try:
        bilans = akcija.balance_sheet
        if not bilans.empty:
            print("\nBilans stanja (poslednja 3 perioda):")
            print(bilans.iloc[:, :3].to_string())
    except Exception as e:
        print(f"  Bilans stanja nije dostupan: {e}")

    try:
        prihodi = akcija.financials
        if not prihodi.empty:
            print("\nDobit i gubitak (poslednja 3 perioda):")
            print(prihodi.iloc[:, :3].to_string())
    except Exception as e:
        print(f"  D&B nije dostupan: {e}")


def main() -> None:
    print("Yahoo Finance - pretraga akcija")
    print("-" * 40)

    while True:
        tiker = input("Unesi tiker akcije (npr. AAPL, MSFT, TSLA) ili 'q' za izlaz: ").strip().upper()
        if tiker in ("Q", "QUIT", "EXIT"):
            print("Izlazim iz programa.")
            break
        if not tiker:
            continue
        try:
            povuci_podatke(tiker)
        except Exception as e:
            print(f"Greška pri povlačenju podataka za {tiker}: {e}")


if __name__ == "__main__":
    main()
