# ekstraklasa-analysis

Analiza statystyczna wyrównania konkurencyjnego (competitive balance) w polskiej Ekstraklasie 25/26 — biblioteka Python + skrypty, które wygenerowały dane i figury do artykułu **"Ekstraklasa 25/26 — losowa czy wyrównana?"**

## Co tu jest

```
src/ekstraklasa/        # biblioteka analityczna
├── config.py           # ścieżki, stałe (LEAGUES, COLORS, TOP5, ALL_SIX, CURRENT_SEASON)
├── data/               # loadery CSV-ek, budowa tabel ligowych
├── metrics/            # ASD, Noll-Scully, Dixon-Coles,
│                       # kalibracja kursów bukmacherskich, statystyki rozkładu
└── plots/              # figury do artykułu (fig3, fig6, fig7, fig14, fig15, fig16, fig17, fig18, fig20)

scripts/                # entry points
data/                   # 11 CSV z football-data.co.uk + cover artykułu
                        # POL.csv (Ekstraklasa 2012-2026) + 5×2 lig Top 5
output/                 # wygenerowane CSV-ki metryk i figury PNG
paper.md                # pełny tekst artykułu (Substack)
```

## Wymagania

Python 3.10+ z `pandas`, `numpy`, `matplotlib`. Bez scipy.

```bash
pip install -r requirements.txt
```

## Uruchomienie

Wszystkie skrypty z `scripts/`:

```bash
cd scripts
python3 01_tables_and_balance.py     # → output/csv/{tables_per_season,league_metrics}.csv
python3 02_cross_league.py           # → output/csv/all_league_metrics.csv
python3 03_figures.py                # → fig3, fig17, fig18
python3 04_dixon_coles_mc.py         # → output/csv/dixon_coles_metrics.csv + fig6, fig7
python3 05_calibration.py            # → output/csv/calibration_metrics.csv
python3 08_distribution_stats.py     # → output/csv/distribution_stats.csv + fig14, fig15
python3 09_slope_chart.py            # → fig16 (slope chart Ekstraklasy)
python3 11_position_changes.py       # → output/csv/position_changes_<league>.csv + fig20
python3 12_goal_stats.py             # → output/csv/team_match_stats_2526_<league>.csv + fig21
```

Skrypty są niezależne, można uruchamiać dowolny w dowolnej kolejności.

Każdy zaczyna się od `import _bootstrap` — to shim, który dodaje `src/` do `sys.path`, więc nie trzeba instalować pakietu.

## Metodologia (skrót)

- **ASD (Actual Standard Deviation)**: odchylenie standardowe punktów w tabeli — najprostszy miernik kompresji.
- **Noll-Scully**: ASD znormalizowane przez ISD (odchylenie hipotetycznej ligi losowej). NS = 1 oznacza ligę nieodróżnialną klasowo. Liczone z poprawką na remisy (q = 0.25).
- **Dixon-Coles**: model Poissona, oddzielnie atak i obrona per drużyna. Klasa = atak + obrona. Closed-form coordinate updates (bez scipy/gradientu).
- **Monte Carlo**: 5000 alternatywnych sezonów per liga z wyestymowanymi klasami DC, losowanie goli z rozkładu Poissona.
- **Kalibracja kursów**: kursy zamknięcia bukmacherów → prawdopodobieństwo no-vig → porównanie z faktycznym wynikiem (Brier, Murphy decomposition).

Pełne wzory i odniesienia literaturowe — patrz `docs/WSKAZNIKI.md` w głównym projekcie [analiza-ekstraklasy](https://github.com/tomasz-morcinek-dtiq/analiza-ekstraklasy).

## Dane

Wszystkie CSV-ki z [football-data.co.uk](https://www.football-data.co.uk/) (Pinnacle Closing, Bet365 Closing, Average Closing odds + wyniki). Pliki w `data/`:

- `POL.csv` — Ekstraklasa, sezony 2012-2026 (z kolumną `Season`)
- `E0.csv` / `E0-2.csv` — EPL 25/26 i 24/25
- `SP1.csv` / `SP1-2.csv` — La Liga 25/26 i 24/25
- `D1.csv` / `D1-2.csv` — Bundesliga 25/26 i 24/25
- `I1.csv` / `I1-2.csv` — Serie A 25/26 i 24/25
- `F1.csv` / `F1-2.csv` — Ligue 1 25/26 i 24/25

## Licencja

MIT — zobacz [LICENSE](LICENSE).

## Artykuł

Pełny tekst polski (Substack): [paper.md](paper.md)
