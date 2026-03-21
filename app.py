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

def is_id_column(col_name, series):
    id_keywords = ['id', 'code', 'number', 'num', 'no', 'key', 'index',
                   'zip', 'phone', 'postal', 'pin', 'sku', 'ref', 'invoice']
    col_lower = col_name.lower().replace(' ', '')
    if any(keyword in col_lower for keyword in id_keywords):
        return True
    if series.nunique() == len(series):
        return True
    if series.dtype in ['int64', 'float64']:
        if series.min() > 1000 and series.max() < 999999 and series.nunique() > 100:
            sample = series.dropna().head(10)
            if all(1000 <= v <= 99999 for v in sample):
                return True
    return False

def get_best_numeric_cols(df):
    priority_keywords = ['sales', 'revenue', 'profit', 'amount', 'price',
                         'cost', 'quantity', 'total', 'income', 'discount']
    numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
    filtered = [col for col in numeric_cols if not is_id_column(col, df[col])]
    priority = []
    others = []
    for col in filtered:
        if any(kw in col.lower() for kw in priority_keywords):
            priority.append(col)
        else:
            others.append(col)
    result = priority + others
    return result if result else numeric_cols

def get_best_categorical_cols(df):
    priority_keywords = ['category', 'region', 'segment', 'type', 'status',
                         'department', 'product', 'country', 'city', 'state',
                         'gender', 'grade', 'class', 'group', 'brand']
    categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
    smart_cols = []
    for col in categorical_cols:
        if is_id_column(col, df[col]):
            continue
        unique_ratio = df[col].nunique() / len(df)
        if unique_ratio > 0.5:
            continue
        date_keywords = ['date', 'time', 'year', 'month', 'day']
        if any(keyword in col.lower() for keyword in date_keywords):
            continue
        smart_cols.append(col)
    priority = []
    others = []
    for col in smart_cols:
        if any(kw in col.lower() for kw in priority_keywords):
            priority.append(col)
        else:
            others.append(col)
    return priority + others

def get_date_col(df):
    date_keywords = ['date', 'time', 'year', 'month', 'day']
    for col in df.columns:
        if any(keyword in col.lower() for keyword in date_keywords):
            try:
                df[col] = pd.to_datetime(df[col])
                return col
            except:
                pass
    return None

def apply_dark_theme(fig):
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
    numeric_cols_temp = df.select_dtypes(include=['int64', 'float64']).columns
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

    numeric_cols = get_best_numeric_cols(df)
    categorical_cols = get_best_categorical_cols(df)
    date_col = get_date_col(df)
    charts = []

    if len(categorical_cols) >= 1 and len(numeric_cols) >= 1:
        cat_col = categorical_cols[0]
        num_col = numeric_cols[0]
        top_data = df.groupby(cat_col)[num_col].sum().nlargest(10).reset_index()
        fig1 = px.bar(top_data, x=cat_col, y=num_col,
                      title=f"{num_col} by {cat_col}",
                      color=num_col,
                      color_continuous_scale='Purples')
        fig1.update_layout(
            paper_bgcolor='#1a1a2e',
            plot_bgcolor='#1a1a2e',
            font_color='#ffffff',
            title_font_color='#a5b4fc',
            xaxis=dict(gridcolor='#2a2a3e', color='#ffffff'),
            yaxis=dict(gridcolor='#2a2a3e', color='#ffffff'),
            coloraxis_showscale=False
        )
        charts.append(json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder))

    if date_col and len(numeric_cols) >= 1:
        num_col = numeric_cols[0]
        trend_data = df.groupby(date_col)[num_col].sum().reset_index()
        fig2 = px.line(trend_data, x=date_col, y=num_col,
                       title=f"{num_col} Trend Over Time",
                       color_discrete_sequence=['#6366f1'])
        charts.append(json.dumps(apply_dark_theme(fig2), cls=plotly.utils.PlotlyJSONEncoder))
    elif len(categorical_cols) >= 2 and len(numeric_cols) >= 1:
        cat_col = categorical_cols[1]
        num_col = numeric_cols[0]
        top_data = df.groupby(cat_col)[num_col].sum().nlargest(10).reset_index()
        fig2 = px.bar(top_data, x=cat_col, y=num_col,
                      title=f"{num_col} by {cat_col}",
                      color_discrete_sequence=['#8b5cf6'])
        fig2.update_layout(
            paper_bgcolor='#1a1a2e',
            plot_bgcolor='#1a1a2e',
            font_color='#ffffff',
            title_font_color='#a5b4fc',
            xaxis=dict(gridcolor='#2a2a3e', color='#ffffff'),
            yaxis=dict(gridcolor='#2a2a3e', color='#ffffff')
        )
        charts.append(json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder))

    if len(numeric_cols) >= 2:
        sample_df = df.sample(min(500, len(df)))
        fig3 = px.scatter(sample_df,
                          x=numeric_cols[0],
                          y=numeric_cols[1],
                          title=f"{numeric_cols[0]} vs {numeric_cols[1]}",
                          color_discrete_sequence=['#a5b4fc'])
        charts.append(json.dumps(apply_dark_theme(fig3), cls=plotly.utils.PlotlyJSONEncoder))

    best_cat = None
    for col in categorical_cols:
        if 2 <= df[col].nunique() <= 10:
            best_cat = col
            break
    if best_cat:
        top_cat = df[best_cat].value_counts().head(8)
        fig4 = px.pie(values=top_cat.values,
                      names=top_cat.index,
                      title=f"Distribution of {best_cat}",
                      color_discrete_sequence=px.colors.sequential.Purples_r)
        fig4.update_layout(
            paper_bgcolor='#1a1a2e',
            font_color='#ffffff',
            title_font_color='#a5b4fc',
            legend=dict(bgcolor='#1a1a2e', font=dict(color='#ffffff'))
        )
        charts.append(json.dumps(fig4, cls=plotly.utils.PlotlyJSONEncoder))

    if len(numeric_cols) >= 1:
        box_cols = numeric_cols[:min(4, len(numeric_cols))]
        fig5 = px.box(df, y=box_cols,
                      title="Outlier Detection - Box Plot",
                      color_discrete_sequence=['#a5b4fc', '#6366f1', '#8b5cf6', '#c4b5fd'])
        charts.append(json.dumps(apply_dark_theme(fig5), cls=plotly.utils.PlotlyJSONEncoder))

    if len(numeric_cols) >= 2:
        corr_cols = numeric_cols[:min(8, len(numeric_cols))]
        corr = df[corr_cols].corr().round(2)
        fig6 = px.imshow(corr,
                         title="Correlation Heatmap",
                         color_continuous_scale='Viridis',
                         text_auto=True,
                         aspect='auto')
        fig6.update_layout(
            paper_bgcolor='#1a1a2e',
            plot_bgcolor='#1a1a2e',
            font_color='#ffffff',
            title_font_color='#a5b4fc',
            width=700,
            height=500
        )
        charts.append(json.dumps(fig6, cls=plotly.utils.PlotlyJSONEncoder))

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

@app.route('/build_chart', methods=['POST'])
def build_chart():
    file = request.files['file']
    x_col = request.form.get('x_col')
    y_col = request.form.get('y_col')
    chart_type = request.form.get('chart_type')
    df = read_file(file)

    try:
        dark_layout = {
            'paper_bgcolor': '#1a1a2e',
            'plot_bgcolor': '#1a1a2e',
            'font': {'color': '#ffffff'},
            'xaxis': {'gridcolor': '#2a2a3e', 'color': '#ffffff'},
            'yaxis': {'gridcolor': '#2a2a3e', 'color': '#ffffff'},
            'legend': {'bgcolor': '#1a1a2e', 'font': {'color': '#ffffff'}}
        }

        if chart_type == 'bar':
            if df[y_col].dtype == 'object':
                return jsonify({'error': f'Y Axis "{y_col}" must be numeric like Sales or Profit.'})
            grouped = df.groupby(x_col)[y_col].sum().reset_index()
            grouped = grouped.sort_values(y_col, ascending=False).head(15)
            chart = {
                'data': [{
                    'type': 'bar',
                    'x': grouped[x_col].tolist(),
                    'y': [round(float(v), 2) for v in grouped[y_col].tolist()],
                    'marker': {'color': '#6366f1'},
                    'name': y_col
                }],
                'layout': {
                    **dark_layout,
                    'title': {'text': f'{y_col} by {x_col}', 'font': {'color': '#a5b4fc'}},
                    'xaxis': {**dark_layout['xaxis'], 'title': x_col},
                    'yaxis': {**dark_layout['yaxis'], 'title': y_col}
                }
            }
            return jsonify({'chart': json.dumps(chart)})

        elif chart_type == 'line':
            if df[y_col].dtype == 'object':
                return jsonify({'error': f'Y Axis "{y_col}" must be numeric like Sales or Profit.'})
            grouped = df.groupby(x_col)[y_col].sum().reset_index()
            chart = {
                'data': [{
                    'type': 'scatter',
                    'mode': 'lines+markers',
                    'x': grouped[x_col].astype(str).tolist(),
                    'y': [round(float(v), 2) for v in grouped[y_col].tolist()],
                    'line': {'color': '#6366f1'},
                    'name': y_col
                }],
                'layout': {
                    **dark_layout,
                    'title': {'text': f'{y_col} over {x_col}', 'font': {'color': '#a5b4fc'}},
                    'xaxis': {**dark_layout['xaxis'], 'title': x_col},
                    'yaxis': {**dark_layout['yaxis'], 'title': y_col}
                }
            }
            return jsonify({'chart': json.dumps(chart)})

        elif chart_type == 'scatter':
            sample = df.sample(min(500, len(df)))
            chart = {
                'data': [{
                    'type': 'scatter',
                    'mode': 'markers',
                    'x': [round(float(v), 2) for v in sample[x_col].tolist()],
                    'y': [round(float(v), 2) for v in sample[y_col].tolist()],
                    'marker': {'color': '#8b5cf6'},
                    'name': f'{x_col} vs {y_col}'
                }],
                'layout': {
                    **dark_layout,
                    'title': {'text': f'{x_col} vs {y_col}', 'font': {'color': '#a5b4fc'}},
                    'xaxis': {**dark_layout['xaxis'], 'title': x_col},
                    'yaxis': {**dark_layout['yaxis'], 'title': y_col}
                }
            }
            return jsonify({'chart': json.dumps(chart)})

        elif chart_type == 'pie':
            counts = df[x_col].value_counts().head(8)
            chart = {
                'data': [{
                    'type': 'pie',
                    'labels': counts.index.tolist(),
                    'values': counts.values.tolist(),
                    'marker': {'colors': ['#6366f1','#8b5cf6','#a5b4fc','#c4b5fd','#4f46e5','#7c3aed','#9333ea','#a855f7']},
                    'textfont': {'color': '#ffffff'}
                }],
                'layout': {
                    'paper_bgcolor': '#1a1a2e',
                    'font': {'color': '#ffffff'},
                    'title': {'text': f'Distribution of {x_col}', 'font': {'color': '#a5b4fc'}},
                    'legend': {'bgcolor': '#1a1a2e', 'font': {'color': '#ffffff'}}
                }
            }
            return jsonify({'chart': json.dumps(chart)})

        elif chart_type == 'box':
            chart = {
                'data': [{
                    'type': 'box',
                    'y': [round(float(v), 2) for v in df[y_col].tolist()],
                    'name': y_col,
                    'marker': {'color': '#a5b4fc'}
                }],
                'layout': {
                    **dark_layout,
                    'title': {'text': f'Box Plot of {y_col}', 'font': {'color': '#a5b4fc'}}
                }
            }
            return jsonify({'chart': json.dumps(chart)})

        elif chart_type == 'histogram':
            chart = {
                'data': [{
                    'type': 'histogram',
                    'x': [round(float(v), 2) for v in df[x_col].tolist()],
                    'marker': {'color': '#6366f1'},
                    'name': x_col
                }],
                'layout': {
                    **dark_layout,
                    'title': {'text': f'Distribution of {x_col}', 'font': {'color': '#a5b4fc'}},
                    'xaxis': {**dark_layout['xaxis'], 'title': x_col}
                }
            }
            return jsonify({'chart': json.dumps(chart)})

    except Exception as e:
        return jsonify({'error': str(e)})

    return jsonify({'error': 'Could not generate chart'})

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

if __name__ == '__main__':
    app.run(debug=True)