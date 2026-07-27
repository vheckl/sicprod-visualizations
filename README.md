# SiCProD Visualizations

Exploratory Streamlit dashboard visualizing data from the SiCProD project
(https://sicprod.acdh.oeaw.ac.at/).

## What's here

- **Gender distribution** — a breakdown of recorded persons by gender.
- **Name search** — search by surname/forename, with fuzzy matching for
  misspellings or historical spelling variation.
- **Marriage network** — a network visualization of marriage relations,
  including a filtered view highlighting individuals who married more than
  once.

## Setup

This project uses [uv](https://realpython.com/python-uv/) for dependency management.

```bash
uv sync
uv run streamlit run sicprod_visualizations.py
```

## Data

`table_person_data.csv` and `table_marriages.csv` contain data derived from
the SiCProD project.