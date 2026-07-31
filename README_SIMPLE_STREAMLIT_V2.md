# Simple Streamlit Bus Dashboard V2

Changes in this version:

- fixed title spacing
- title is fully visible below the Streamlit toolbar
- added Light and Dark mode toggle
- map style follows the selected mode
- cards, text, filters and route panels follow the selected mode
- kept the same simple one-page layout

## Replace these files

Copy into the project root:

- streamlit_app.py
- dashboard_data.json
- requirements.txt
- .gitignore
- .streamlit/config.toml
- .streamlit/secrets.toml.example

Keep your existing:

- .streamlit/secrets.toml
- .env

## Run

```bash
cd ~/Desktop/bus-disruption-platform
conda activate pyspark35
python -m pip install -r requirements.txt
streamlit run streamlit_app.py
```
