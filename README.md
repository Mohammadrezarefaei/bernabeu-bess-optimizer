# Santiago Bernabéu BESS Financial & Energy Dashboard

A bankable valuation and energy optimization platform designed to evaluate utility-scale Battery Energy Storage Systems (BESS) across different architectural zones and operating scenarios at the Santiago Bernabéu stadium.

🌐 **Live Demo:** [View Streamlit Dashboard](https://bernabeu-bess-optimizer-bib7uw2scelgkqsagdwcmn.streamlit.app/)  
📂 **GitHub Repository:** [Mohammadrezarefaei/bernabeu-bess-optimizer](https://github.com/Mohammadrezarefaei/bernabeu-bess-optimizer/tree/main)

---

## Key Features

* **Zone-Specific Load Profiling:** Models power demand across distinct stadium stands (Lateral Oeste, Lateral Este, Fondo Norte, and Fondo Sur) using custom load multipliers and event scenarios.
* **Peak Shaving Optimization:** Solves daily power dispatch vectors to reduce grid strain, shave peak loads, and maximize cost savings.
* **Bankable Financial Modeling:** Evaluates project feasibility through a 70/30 debt-to-equity financing structure, calculating total CAPEX, bank debt, equity requirements, and the Debt Service Coverage Ratio (DSCR).
* **Interactive Web Interface:** Built with Streamlit featuring a dark-themed UI, dynamic power/energy sliders, automated 24-hour dispatch curve plotting, and stadium layout visualization.

---

## Tech Stack

* **Frontend / Dashboard:** Streamlit, Matplotlib, PIL (Pillow)
* **Data Processing & Math:** Pandas, NumPy
* **Optimization & Financials:** Custom modular backend (`models/optimizer.py`, `models/financials.py`, `utils/scenarios.py`)

---

## Project Structure

```text
bernabeu-bess-optimizer/
│
├── data/                    # Market and parameter configuration files
│   └── market_params.json   # Base electricity pricing and demand charges
├── models/                  # Core calculation and optimization engines
│   ├── __init__.py
│   ├── financials.py        # CAPEX, debt/equity, and DSCR calculations
│   └── optimizer.py         # Peak shaving and BESS dispatch logic
├── utils/                   # Helper modules and scenario generators
│   ├── __init__.py
│   └── scenarios.py         # Stadium load profile generators (Match Day, Concert, etc.)
├── app.py                   # Main Streamlit dashboard application
├── bernabeu_layout.png      # Stadium zone mapping visual asset
├── requirements.txt         # Required Python packages
└── README.md                # Project documentation
