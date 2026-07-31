# Simple Streamlit Bus Dashboard

This version uses one clean page only.

It contains:

- four KPI cards
- route search
- priority filter
- near-live vehicle map
- saved route-priority locations
- eight highest-priority routes
- one priority chart
- one route-ranking table

## Replace the current Streamlit files

Copy into the root of `bus-disruption-platform`:

- streamlit_app.py
- dashboard_data.json
- requirements.txt
- .gitignore
- .streamlit/config.toml
- .streamlit/secrets.toml.example

Keep or create:

`.streamlit/secrets.toml`

Use:

```toml
BODS_API_KEY = "your_real_api_key"
BODS_FEED_ID = "10609"
```

The app also checks the existing `.env` file when running locally.

## Run

```bash
cd ~/Desktop/bus-disruption-platform
conda activate pyspark35
python -m pip install -r requirements.txt
streamlit run streamlit_app.py
```

Open:

`http://localhost:8501`

## Important

The map shows vehicle points and representative route-recovery locations.
It does not draw full route lines because the saved project data contains
one map centre for each route-direction result rather than an ordered route shape.
