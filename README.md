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

# część 2 — „Co ściska tabelę Ekstraklasy?" (paper2.md)
python3 27_fear_per_team.py          # → output/csv/teams/fear_per_team.csv (strefa strachu per drużyna)
python3 35_possession_last_k.py      # → fig66, fig66b (posiadanie per drużyna / Lech)
python3 40_margin_three_leagues.py   # → fig95 (rozkład różnicy bramek, 3 ligi)
python3 41_h2h_three_leagues.py      # → fig96 (macierze H2H + cykle)
python3 44_style_dispersion.py       # → output/csv/style/style_dispersion.csv (CV rozrzutu stylu)
python3 45_style_outliers.py         # → output/csv/style/style_outliers.csv (outliery 0/0/2)
python3 47_possession_figs.py        # → fig116, fig117 (posiadanie a wynik/prowadzenie)
python3 48_style_chapter_figs.py     # → fig89, fig90 (boxplot posiadania, cechy stylu)
python3 49_first_goal_loss_rate.py   # → output/csv/leagues/first_goal_loss_rate.csv (≥60% pos., straty)
python3 50_first_goal_value.py       # → output/csv/leagues/first_goal_value.csv (pierwszy gol → wynik)
python3 51_first_goal_by_favourite.py# → output/csv/leagues/first_goal_favourite{,_bands}.csv + fig118, fig119
python3 52_high_possession_table.py  # → output/csv/leagues/high_possession_table.csv (tabela ≥60%)
python3 54_zone_composition.py       # → fig123 (kompozycja strefy strachu)
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
