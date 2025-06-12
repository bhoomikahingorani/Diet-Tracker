# 🥗 Enhanced Diet Analysis App

This is a **Streamlit-based web application** for analyzing and visualizing dietary data. It provides users with insightful charts, downloadable reports, and customized feedback to help track and enhance dietary habits.

---

## 🚀 Features

- 📊 **Interactive Data Upload & Display**: Upload Excel files containing food consumption data and view them in a dynamic table.
- 🧮 **Nutrient Analysis**: Compare your nutrient intake against recommended values (RDA).
- 📈 **Visual Insights**: Interactive charts using Plotly and Altair to explore macro/micronutrient data.
- 📥 **Downloadable Reports**: Export filtered or full datasets as downloadable Excel files.
- 🌐 **Timezone and Date Handling**: Robust date handling for accurate timeline visualizations.

---

## 🛠️ Tech Stack

- **Frontend & Backend**: [Streamlit](https://streamlit.io/)
- **Data Processing**: Pandas, NumPy
- **Visualization**: Plotly, Altair, Seaborn, Matplotlib
- **Excel Support**: Openpyxl, Xlrd
- **Deployment**: Gunicorn (for production server environments)

---

## 📦 Installation

Clone the repository:

```bash
git clone https://github.com/bhoomikahingorani/Diet-Tracker.git
cd Diet-Tracker
```
Create a virtual environment 

```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```
Install the dependencies

```bash
pip install -r requirements.txt
```
Running the App Locally

```bash
streamlit run enhanced_diet_app.py
```
