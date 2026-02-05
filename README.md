# Airline Flight Delay Analysis (USA)

**Ishak Islam** | UMID28072552431 | Unified Mentor Internship

## About

Analysis of airline flight delays in the United States using data from the Bureau of Transportation Statistics (BTS). The analysis covers delay patterns by airport, time periods, and delay causes from 2003-2016.

## How to Run

```bash
pip install -r requirements.txt
jupyter notebook notebooks/01_flight_delay_analysis.ipynb
```

Run all cells to generate the analysis and visualizations.

## Dataset

**Source:** CORGIS Dataset Project (Bureau of Transportation Statistics)

**URL:** https://corgis-edu.github.io/corgis/datasets/csv/airlines/airlines.csv

The dataset (`airlines.csv`) is already included in the `data/` folder.

## Project Structure

```
├── data/              # Dataset file (airlines.csv)
├── notebooks/         # Jupyter analysis notebook
├── scripts/           # Python helper modules
├── visualizations/    # Generated charts (PNG)
├── tableau/           # Tableau data exports (CSV)
└── docs/              # Quick start documentation
```

## Analysis Outputs

- Yearly delay trend (2003-2016)
- Monthly delay patterns
- Airport performance comparison (29 major airports)
- Delay cause breakdown (Carrier, Late Aircraft, NAS, Weather, Security)
- Cancellation patterns
- Tableau-ready data exports

## Tableau Dashboard

Interactive dashboard available at: [Tableau Public](https://public.tableau.com/app/profile/ishak.islam/viz/AirlineFlightDelayAnalysisUSA/Dashboard?publish=yes)

## Technologies

Python, Pandas, NumPy, Matplotlib, Seaborn, Tableau

## GitHub Repository

**Source Code:** [https://github.com/isacmj7/airline-flight-delay-analysis](https://github.com/isacmj7/airline-flight-delay-analysis)
