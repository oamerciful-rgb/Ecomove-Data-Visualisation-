# EcoMove Mobility – Data Visualisation Investigation

MSc Data Science, Arden University – COM7021 Data Visualisation

A Python investigation of urban transport performance across 12 European cities
(2024–2025): demand, service reliability, cost recovery, accessibility and CO₂ savings,
with an interactive Plotly Dash dashboard designed for senior managers.

## Contents
- `Data_Visualisation.ipynb` – data loading, cleaning, data-quality audit and nine charts
- `dashboard_revised_colab.py` – interactive dashboard (8 KPIs, 6 filters, 6 linked charts)
- `fig1` … `fig9` – exported charts
- `dashboard_default.png`, `dashboard_bus_snow.png` – dashboard screenshots

## Key findings
- Demand per record was stable year on year; raw totals were distorted by unequal sampling
- Berlin and Paris have the highest demand per service record
- Fares cover 99.6% of network costs; Bike Share and E-Scooter recover under 8% of their costs
- Delay is the measure most strongly linked to customer rating (r = −0.82)
- Snow more than doubles typical delay; event days raise demand by about 26%
- Bus and E-Scooter users report the most accessibility complaints per passenger

## How to run
1. Install: `pip install pandas numpy matplotlib seaborn openpyxl dash plotly`
2. Open the notebook in Google Colab and upload the dataset
3. Click Runtime → Run all
4. Run the dashboard cell to open the interactive dashboard

## Data
The dataset is provided by Arden University for assessment purposes and is not
redistributed here.

## Tools
Python · pandas · NumPy · Matplotlib · Seaborn · Plotly Dash · Google Colab
