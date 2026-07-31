# Streamlit Bus Dashboard from Scratch

This package does not use the old `dashboard` folder.

## Put these files in the project root

- streamlit_app.py
- dashboard_data.json
- requirements.txt
- .gitignore
- .streamlit/config.toml
- .streamlit/secrets.toml.example

## Create the real secrets file

Create:

`.streamlit/secrets.toml`

Paste:

```toml
BODS_API_KEY = "your_real_api_key"
BODS_FEED_ID = "10609"
```

Never upload this file to GitHub.

## Run locally

```bash
cd ~/Desktop/bus-disruption-platform
conda activate pyspark35
python -m pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Publish on Streamlit Community Cloud

Push these files to GitHub:

- streamlit_app.py
- dashboard_data.json
- requirements.txt
- .gitignore
- .streamlit/config.toml
- .streamlit/secrets.toml.example

Do not push:

- .env
- .streamlit/secrets.toml

Set the main file path to:

`streamlit_app.py`

Add these secrets in Streamlit Advanced settings:

```toml
BODS_API_KEY = "your_real_api_key"
BODS_FEED_ID = "10609"
```

## What is near-live

Blue map points are vehicle locations downloaded from BODS and refreshed
approximately every 60 seconds.

The model predictions and recovery priorities are loaded from
`dashboard_data.json`.
