# Bus Disruption Severity Prediction and Route Recovery Priority Platform Using PySpark

## Project Overview

This project predicts bus disruption severity and generates route recovery priorities using PySpark and Machine Learning. It combines scheduled timetable information with real-time vehicle location data to help transport operators identify routes that require immediate operational attention.

The system processes large-scale transport datasets, engineers disruption-related features, trains multiple machine learning models, and presents the results through an interactive Streamlit dashboard.

---

## Objectives

- Collect and process large-scale public transport datasets.
- Integrate scheduled timetable and live vehicle location data.
- Engineer meaningful disruption features.
- Predict disruption severity using supervised machine learning.
- Rank affected routes based on recovery priority.
- Provide an interactive dashboard for transport operators.

---

## Dataset

### 1. West Midlands GTFS Timetable
Contains scheduled public transport information including:

- Routes
- Trips
- Stop Times
- Stops
- Calendar

### 2. National Express West Midlands SIRI-VM Feed

Provides near-live vehicle location data including:

- Vehicle Reference
- Line Reference
- Direction
- Operator
- Latitude
- Longitude
- Recorded Time

---

## Technologies Used

- Python
- PySpark
- Spark SQL
- Spark MLlib
- Pandas
- Streamlit
- Jupyter Notebook
- Git
- GitHub

---

## Machine Learning Models

The project compares three supervised learning algorithms:

- Logistic Regression
- Decision Tree
- Random Forest

Random Forest achieved the best overall performance and was selected as the final prediction model.

---

## Project Workflow

1. Vehicle Location Data Collection
2. GTFS Timetable Loading
3. Data Cleaning and Preprocessing
4. Dataset Joining
5. Feature Engineering
6. Exploratory Data Analysis
7. PySpark SQL Analysis
8. Machine Learning Model Training
9. Route Recovery Priority Generation
10. Streamlit Dashboard Deployment

---

## Project Structure

```
bus-disruption-platform/
│
├── data/
│   ├── raw/
│   └── processed/
│
├── notebooks/
│   ├── 01_vehicle_location_collection.ipynb
│   ├── 02_timetable_preprocessing.ipynb
│   ├── 03_vehicle_location_preprocessing.ipynb
│   ├── 04_dataset_joining.ipynb
│   ├── 05_disruption_feature_engineering.ipynb
│   ├── 06_exploratory_data_analysis.ipynb
│   ├── 07_pyspark_sql_analysis.ipynb
│   ├── 08_model_training_evaluation.ipynb
│   ├── 09_route_recovery_priority.ipynb
│
├── streamlit_app.py
├── requirements.txt
└── README.md
```

---

## Running the Project

### Activate Environment

```bash
conda activate pyspark35
```

### Navigate to Project Folder

```bash
cd ~/Desktop/bus-disruption-platform
```

### Launch Dashboard

```bash
streamlit run streamlit_app.py
```

The dashboard will be available at:

```
http://localhost:8501
```

---

## Dashboard Features

- Project KPI Summary
- Route Search
- Priority Filtering
- Interactive Route Map
- Near-live Vehicle Locations
- Route Recovery Priority Ranking
- Priority Distribution Charts
- Machine Learning Prediction Results

---

## Machine Learning Performance

The Random Forest model achieved the highest overall performance among the evaluated models and was selected for predicting disruption severity.

Evaluation metrics include:

- Accuracy
- Precision
- Recall
- Weighted F1-score

---

## Future Improvements

- Real-time streaming using Spark Structured Streaming
- Weather data integration
- Passenger demand prediction
- Automatic model retraining
- Multi-city deployment
- Explainable AI techniques

---

## Author

**Babita Adhikari**

ST5011CEM – Big Data Programming Coursework

---

## Acknowledgements

- UK Bus Open Data Service (BODS)
- National Express West Midlands
- Apache Spark
- Streamlit
- University Coursework Module
