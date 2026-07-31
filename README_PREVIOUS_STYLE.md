# Previous-Style Streamlit Dashboard

This package recreates the earlier dark dashboard in Streamlit with:

- navy sidebar navigation
- Overview, Map, Analytics, Models and Ranking pages
- near-live BODS vehicle markers refreshed every 60 seconds
- saved route-recovery priority circles
- highest-priority route panel
- model comparison and feature importance
- route filters and CSV download

## Copy into the project root

Replace the simpler Streamlit files with:

- `streamlit_app.py`
- `dashboard_data.json`
- `requirements.txt`
- `.gitignore`
- `.streamlit/config.toml`
- `.streamlit/secrets.toml.example`

Keep or recreate `.streamlit/secrets.toml`:

```toml
BODS_API_KEY = "your_real_api_key"
BODS_FEED_ID = "10609"
```

Run:

```bash
cd ~/Desktop/bus-disruption-platform
conda activate pyspark35
python -m pip install -r requirements.txt
streamlit run streamlit_app.py
```
