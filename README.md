# 🎓 KEA Engineering College Predictor Dashboard

A Streamlit-based web application designed to help students predict their engineering college admission chances based on actual Karnataka Examination Authority (KEA) cutoffs and seat matrices. 

## ✨ Features

- **🎯 Smart College Prediction**: Input your CET rank, category, preferred cities, and branches to get personalized college recommendations.
- **📊 Multi-Round Analysis**: Compare cutoffs between Round 1 and Round 3 to understand trends.
- **🟢 Chance Classification**: Recommendations are smartly categorized into:
  - **Safe**: High probability of admission.
  - **Moderate**: Good chances, but highly competitive.
  - **Dream**: Ambitious choices where admission is possible but less likely.
- **📈 Cutoff Trends**: Visualize how cutoffs have shifted for different colleges and branches over rounds.
- **🪑 Seat Matrix Explorer**: Detailed breakdown of available seats across different categories, colleges, and branches.
- **💡 Smart Insights**: Get automated insights based on your prediction results (e.g., trend relaxations, most common branches in your range).

## 🛠️ Technology Stack

- **Frontend & App Framework**: [Streamlit](https://streamlit.io/)
- **Data Manipulation**: Pandas, NumPy
- **Data Visualization**: Plotly Express
- **Data Extraction**: pdfplumber, openpyxl (used for extracting and cleaning data from official KEA PDFs)

## 📂 Project Structure

```text
kea_dashboard/
├── app.py                 # Main application entry point (Predictor)
├── pages/                 # Additional dashboard pages
│   ├── 2_Cutoff_Trends.py # Trends visualization page
│   ├── 3_Seat_Matrix.py   # Seat availability explorer
│   └── 4_Analytics.py     # General KCET analytics
├── utils/                 # Helper functions and core logic
│   ├── data_loader.py     # Handles loading cleaned data
│   ├── predictor.py       # Prediction algorithm and chance classification
│   ├── clean_data.py      # Data cleaning and normalization pipeline
│   └── ui_components.py   # Reusable Streamlit UI components and CSS
├── scripts/               # Utility scripts (e.g., testing data extraction)
├── data/                  # Cleaned datasets used by the app
├── assets/                # Images or static assets
├── styles/                # CSS styling files
└── requirements.txt       # Python dependencies
```

## 🚀 How to Run Locally

### 1. Prerequisites
Ensure you have Python installed on your local machine.

### 2. Create a Virtual Environment (Optional but Recommended)
It is recommended to run the app inside a virtual environment to manage dependencies cleanly.
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies
Install the required Python packages from `requirements.txt`:
```bash
pip install -r requirements.txt
```

### 4. Run the Application
Navigate to the project root directory and run the Streamlit app:
```bash
streamlit run app.py
```
This will start the local server and open the dashboard in your default web browser (usually at `http://localhost:8501`).

## 🧹 Data Processing
The data driving this dashboard is extracted directly from the official KEA PDFs. The `utils/clean_data.py` pipeline standardizes city names, handles fragmented PDF text, and merges the datasets into a reliable format for the prediction engine.
