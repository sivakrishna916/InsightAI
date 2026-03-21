import json
import plotly
import plotly.express as px
from utils.column_utils import get_best_numeric_cols, get_best_categorical_cols, get_date_col


DARK_LAYOUT = {
    'paper_bgcolor': '#1a1a2e',
    'plot_bgcolor': '#1a1a2e',
    'font': {'color': '#ffffff'},
    'xaxis': {'gridcolor': '#2a2a3e', 'color': '#ffffff'},
    'yaxis': {'gridcolor': '#2a2a3e', 'color': '#ffffff'},
    'legend': {'bgcolor': '#1a1a2e', 'font': {'color': '#ffffff'}}
}


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


def generate_auto_charts(df):
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

    return charts


def build_custom_chart(df, x_col, y_col, chart_type):
    try:
        if chart_type == 'bar':
            if df[y_col].dtype == 'object':
                return None, f'Y Axis "{y_col}" must be numeric like Sales or Profit.'
            grouped = df.groupby(x_col)[y_col].sum().reset_index()
            grouped = grouped.sort_values(y_col, ascending=False).head(15)
            chart = {
                'data': [{'type': 'bar',
                          'x': grouped[x_col].tolist(),
                          'y': [round(float(v), 2) for v in grouped[y_col].tolist()],
                          'marker': {'color': '#6366f1'},
                          'name': y_col}],
                'layout': {**DARK_LAYOUT,
                           'title': {'text': f'{y_col} by {x_col}', 'font': {'color': '#a5b4fc'}},
                           'xaxis': {**DARK_LAYOUT['xaxis'], 'title': x_col},
                           'yaxis': {**DARK_LAYOUT['yaxis'], 'title': y_col}}
            }
            return json.dumps(chart), None

        elif chart_type == 'line':
            if df[y_col].dtype == 'object':
                return None, f'Y Axis "{y_col}" must be numeric like Sales or Profit.'
            grouped = df.groupby(x_col)[y_col].sum().reset_index()
            chart = {
                'data': [{'type': 'scatter',
                          'mode': 'lines+markers',
                          'x': grouped[x_col].astype(str).tolist(),
                          'y': [round(float(v), 2) for v in grouped[y_col].tolist()],
                          'line': {'color': '#6366f1'},
                          'name': y_col}],
                'layout': {**DARK_LAYOUT,
                           'title': {'text': f'{y_col} over {x_col}', 'font': {'color': '#a5b4fc'}},
                           'xaxis': {**DARK_LAYOUT['xaxis'], 'title': x_col},
                           'yaxis': {**DARK_LAYOUT['yaxis'], 'title': y_col}}
            }
            return json.dumps(chart), None

        elif chart_type == 'scatter':
            sample = df.sample(min(500, len(df)))
            chart = {
                'data': [{'type': 'scatter',
                          'mode': 'markers',
                          'x': [round(float(v), 2) for v in sample[x_col].tolist()],
                          'y': [round(float(v), 2) for v in sample[y_col].tolist()],
                          'marker': {'color': '#8b5cf6'},
                          'name': f'{x_col} vs {y_col}'}],
                'layout': {**DARK_LAYOUT,
                           'title': {'text': f'{x_col} vs {y_col}', 'font': {'color': '#a5b4fc'}},
                           'xaxis': {**DARK_LAYOUT['xaxis'], 'title': x_col},
                           'yaxis': {**DARK_LAYOUT['yaxis'], 'title': y_col}}
            }
            return json.dumps(chart), None

        elif chart_type == 'pie':
            counts = df[x_col].value_counts().head(8)
            chart = {
                'data': [{'type': 'pie',
                          'labels': counts.index.tolist(),
                          'values': counts.values.tolist(),
                          'marker': {'colors': ['#6366f1', '#8b5cf6', '#a5b4fc', '#c4b5fd',
                                                '#4f46e5', '#7c3aed', '#9333ea', '#a855f7']},
                          'textfont': {'color': '#ffffff'}}],
                'layout': {'paper_bgcolor': '#1a1a2e',
                           'font': {'color': '#ffffff'},
                           'title': {'text': f'Distribution of {x_col}', 'font': {'color': '#a5b4fc'}},
                           'legend': {'bgcolor': '#1a1a2e', 'font': {'color': '#ffffff'}}}
            }
            return json.dumps(chart), None

        elif chart_type == 'box':
            chart = {
                'data': [{'type': 'box',
                          'y': [round(float(v), 2) for v in df[y_col].tolist()],
                          'name': y_col,
                          'marker': {'color': '#a5b4fc'}}],
                'layout': {**DARK_LAYOUT,
                           'title': {'text': f'Box Plot of {y_col}', 'font': {'color': '#a5b4fc'}}}
            }
            return json.dumps(chart), None

        elif chart_type == 'histogram':
            chart = {
                'data': [{'type': 'histogram',
                          'x': [round(float(v), 2) for v in df[x_col].tolist()],
                          'marker': {'color': '#6366f1'},
                          'name': x_col}],
                'layout': {**DARK_LAYOUT,
                           'title': {'text': f'Distribution of {x_col}', 'font': {'color': '#a5b4fc'}},
                           'xaxis': {**DARK_LAYOUT['xaxis'], 'title': x_col}}
            }
            return json.dumps(chart), None

    except Exception as e:
        return None, str(e)

    return None, 'Could not generate chart'