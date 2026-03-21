from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

from services.data_service import read_file, get_data_quality
from services.ai_service import get_insights, answer_question
from services.chart_service import generate_auto_charts, build_custom_chart

load_dotenv()

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/analyze', methods=['POST'])
def analyze():
    file = request.files['file']
    df = read_file(file)
    stats = get_data_quality(df)
    charts = generate_auto_charts(df)
    insights = get_insights(df, stats['missing'], stats['duplicates'])

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

    chart, error = build_custom_chart(df, x_col, y_col, chart_type)

    if error:
        return jsonify({'error': error})
    return jsonify({'chart': chart})


@app.route('/chat', methods=['POST'])
def chat():
    file = request.files['file']
    question = request.form.get('question')
    df = read_file(file)
    answer = answer_question(df, question)
    return jsonify({'answer': answer})


if __name__ == '__main__':
    app.run(debug=True)