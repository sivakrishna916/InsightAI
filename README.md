# 🧠 InsightAI – AI-Powered Data Analysis Platform

![Python](https://img.shields.io/badge/Python-3.10-blue)
![Flask](https://img.shields.io/badge/Flask-App-green)
![AI](https://img.shields.io/badge/AI-LLM-orange)
![Status](https://img.shields.io/badge/Status-Active-success)

> Turn raw datasets into **actionable insights in seconds** using AI-powered analysis, visualization, and conversational querying.

---

## 🚀 Live Demo

[👉 Click here to try InsightAI](https://insightai-ir1j.onrender.com)

---

## 🎯 Problem Statement

Data analysis is often time-consuming and requires technical expertise.
InsightAI simplifies this by enabling users to generate insights, visualizations, and answers instantly using AI.

---

## ✨ Features

- 📂 Upload CSV or Excel datasets
- 📊 6 Automatic Data Quality Metrics (Rows, Columns, Missing Values, Duplicates, Outliers, Quality Score)
- 📈 6 Smart Auto Charts (Bar, Scatter, Box Plot, Correlation Heatmap, Pie Chart, Line)
- 🛠️ Interactive Chart Builder — build custom charts by selecting columns and chart type
- 🤖 AI Generated Business Insights powered by Groq LLaMA 3.3 70B
- 💬 Chat with Your Data in Plain English
- 💡 AI Smart Suggestions based on your dataset
- 🔍 Automatic Outlier Detection using IQR method
- 📋 Data Preview Table

---

## 🧠 How It Works

1. User uploads dataset (CSV/Excel)
2. Backend processes data using Pandas
3. Smart heuristics identify useful columns (numeric/categorical)
4. Data quality metrics are computed (missing, duplicates, outliers)
5. Plotly generates dynamic visualizations
6. LLM analyzes dataset and generates insights
7. Chat interface enables natural language queries

---

## 🏗️ Project Structure
```
InsightAI/
│
├── app.py                  # Flask routes only
│
├── services/
│   ├── data_service.py     # File reading, data quality metrics
│   ├── ai_service.py       # Groq AI calls, insights, Q&A
│   └── chart_service.py    # Auto charts, custom chart builder
│
├── utils/
│   └── column_utils.py     # Smart column detection logic
│
├── templates/
│   └── index.html
│
└── static/
    └── style.css
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask |
| Frontend | HTML, CSS, JavaScript |
| Data Analysis | Pandas, Plotly |
| AI | Groq API (LLaMA 3.3 70B) |
| Architecture | Modular — services + utils layers |
| Deployment | Render |

---

## ⚙️ Installation
```bash
# Clone the repository
git clone https://github.com/sivakrishna916/InsightAI.git
cd InsightAI

# Install dependencies
pip install -r requirements.txt

# Create .env file
echo GROQ_API_KEY=your_key_here > .env

# Run the app
python app.py
```

---

## 📸 Screenshots

### Upload Dataset
![Upload](screenshots/upload.png)

### Data Quality Dashboard
![Dashboard](screenshots/dashboard.png)

### Auto Charts
![Charts](screenshots/charts.png)

### AI Insights
![Insights](screenshots/aiinsights.png)

### Chat with Data
![Chat](screenshots/chatbot.png)

---

## 💡 What Makes This Project Stand Out

- Combines AI + Data Analysis + Visualization in one platform
- Automatically generates insights (not just charts)
- Smart column detection filters irrelevant fields automatically
- Enables natural language interaction with datasets
- Modular architecture with clean separation of concerns
- Designed as a mini SaaS product, not just a demo

---

## ⚡ Future Improvements

- 📄 Export reports as PDF or Excel
- 🔐 User authentication and saved datasets
- ⚡ Async processing for large datasets
- 🌐 React frontend for better interactivity

---

## 🧩 Challenges Faced

- Handling CSV files with different encodings automatically
- Building smart heuristics to filter ID columns and irrelevant fields
- Plotly Express JSON structure required raw chart objects for correct rendering
- Refactored from single file to modular services/utils architecture

---

## 💼 Use Cases

- Business analysts exploring sales data
- Students analyzing research datasets
- Anyone who wants instant AI insights from their data

---

## 🙋‍♂️ Author

**Sivakrishna Reddy**
- GitHub: [@sivakrishna916](https://github.com/sivakrishna916)
- LinkedIn: [https://www.linkedin.com/in/sivakrishna-reddy-annem-8a16a3283/]

---

## ⭐ If you find this project useful, please give it a star!