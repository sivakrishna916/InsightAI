from flask import Flask, render_template, request, jsonify
import pandas as pd
import json
import plotly
import plotly.express as px
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def read_file(file):
    if file.filename.endswith('.csv'):
        try:
            df = pd.read_csv(file, encoding='utf-8')
        except UnicodeDecodeError:
            file.seek(0)
            df = pd.read_csv(file, encoding='latin1')
    else:
        df = pd.read_excel(file)
    return df

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    file = request.files['file']
    df = read_file(file)

    duplicates = int(df.duplicated().sum())
    missing = int(df.isnull().sum().sum())

    outlier_count = 0
    numeric_cols_temp = df.select_dtypes(include=['int64','float64']).columns
    for col in numeric_cols_temp:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        outliers = ((df[col] < (Q1 - 1.5 * IQR)) | (df[col] > (Q3 + 1.5 * IQR))).sum()
        outlier_count += int(outliers)

    total_cells = df.shape[0] * df.shape[1]
    quality_score = round(100 - ((missing + duplicates) / total_cells * 100), 1)

    stats = {
        'rows': int(df.shape[0]),
        'columns': int(df.shape[1]),
        'missing': missing,
        'duplicates': duplicates,
        'outliers': outlier_count,
        'quality_score': quality_score,
        'column_names': list(df.columns)
    }

    numeric_cols = df.select_dtypes(include=['int64','float64']).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
    charts = []

    def style_fig(fig):
        fig.update_layout(
            paper_bgcolor='#1a1a2e',
            plot_bgcolor='#1a1a2e',
            font_color='#ffffff',
            title_font_color='#a5b4fc',
            xaxis=dict(gridcolor='#2a2a3e', color='#ffffff'),
            yaxis=dict(gridcolor='#2a2a3e', color='#ffffff'),
            legend=dict(bgcolor='#1a1a2e', font=dict(color='#ffffff'))
        )
        return fig

    if len(numeric_cols) >= 1:
        fig1 = px.histogram(df, x=numeric_cols[0],
                            title=f"Distribution of {numeric_cols[0]}",
                            color_discrete_sequence=['#6366f1'])
        charts.append(json.dumps(style_fig(fig1), cls=plotly.utils.PlotlyJSONEncoder))

    if len(numeric_cols) >= 2:
        fig2 = px.scatter(df, x=numeric_cols[0], y=numeric_cols[1],
                          title=f"{numeric_cols[0]} vs {numeric_cols[1]}",
                          color_discrete_sequence=['#8b5cf6'])
        charts.append(json.dumps(style_fig(fig2), cls=plotly.utils.PlotlyJSONEncoder))

    if len(numeric_cols) >= 1:
        fig3 = px.box(df, y=numeric_cols[:min(4, len(numeric_cols))],
                      title="Outlier Detection - Box Plot",
                      color_discrete_sequence=['#a5b4fc', '#6366f1', '#8b5cf6', '#c4b5fd'])
        charts.append(json.dumps(style_fig(fig3), cls=plotly.utils.PlotlyJSONEncoder))

    if len(numeric_cols) >= 2:
        corr = df[numeric_cols].corr()
        fig4 = px.imshow(corr,
                         title="Correlation Heatmap",
                         color_continuous_scale='Viridis',
                         text_auto=True)
        fig4.update_layout(
            paper_bgcolor='#1a1a2e',
            plot_bgcolor='#1a1a2e',
            font_color='#ffffff',
            title_font_color='#a5b4fc'
        )
        charts.append(json.dumps(fig4, cls=plotly.utils.PlotlyJSONEncoder))

    if len(categorical_cols) >= 1:
        top_cat = df[categorical_cols[0]].value_counts().head(8)
        fig5 = px.pie(values=top_cat.values,
                      names=top_cat.index,
                      title=f"Distribution of {categorical_cols[0]}",
                      color_discrete_sequence=px.colors.sequential.Purples_r)
        fig5.update_layout(
            paper_bgcolor='#1a1a2e',
            font_color='#ffffff',
            title_font_color='#a5b4fc',
            legend=dict(bgcolor='#1a1a2e', font=dict(color='#ffffff'))
        )
        charts.append(json.dumps(fig5, cls=plotly.utils.PlotlyJSONEncoder))

    summary = f"""
    Dataset has {df.shape[0]} rows and {df.shape[1]} columns.
    Columns: {list(df.columns)}
    Missing values: {missing}
    Duplicate rows: {duplicates}
    Numeric summary:
    {df.describe().to_string()}
    """

    prompt = f"""
    You are a professional data analyst. Analyze this dataset and give 5 clear business insights.
    Be specific, mention actual numbers from the data.
    Format each insight on a new line starting with a bullet point.
    {summary}
    """

    ai_response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    insights = ai_response.choices[0].message.content

    return jsonify({
        'stats': stats,
        'charts': charts,
        'preview': df.head(5).to_html(classes='preview-table'),
        'insights': insights
    })

@app.route('/chat', methods=['POST'])
def chat():
    file = request.files['file']
    question = request.form.get('question')
    df = read_file(file)

    summary = f"""
    Dataset has {df.shape[0]} rows and {df.shape[1]} columns.
    Columns: {list(df.columns)}
    Sample data:
    {df.head(10).to_string()}
    Numeric summary:
    {df.describe().to_string()}
    """

    prompt = f"""
    You are a data analyst assistant. Answer this question about the dataset clearly and concisely.
    Question: {question}
    Dataset info:
    {summary}
    """

    ai_response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )

    return jsonify({'answer': ai_response.choices[0].message.content})