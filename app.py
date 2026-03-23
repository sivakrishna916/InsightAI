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
    try:
        file = request.files.get('file')
        if not file or file.filename == '':
            return jsonify({'error': 'No file uploaded.'}), 400

        df, error = read_file(file)
        if error:
            return jsonify({'error': error}), 400

        stats = get_data_quality(df)
        charts = generate_auto_charts(df)
        insights = get_insights(df, stats['missing'], stats['duplicates'])

        return jsonify({
            'stats': stats,
            'charts': charts,
            'preview': df.head(5).to_html(classes='preview-table'),
            'insights': insights
        })

    except Exception as e:
        return jsonify({'error': f'Something went wrong: {str(e)}'}), 500


@app.route('/build_chart', methods=['POST'])
def build_chart():
    try:
        file = request.files.get('file')
        if not file or file.filename == '':
            return jsonify({'error': 'No file uploaded.'}), 400

        x_col = request.form.get('x_col')
        y_col = request.form.get('y_col')
        chart_type = request.form.get('chart_type')

        df, error = read_file(file)
        if error:
            return jsonify({'error': error}), 400

        chart, error = build_custom_chart(df, x_col, y_col, chart_type)
        if error:
            return jsonify({'error': error})

        return jsonify({'chart': chart})

    except Exception as e:
        return jsonify({'error': f'Something went wrong: {str(e)}'}), 500


@app.route('/chat', methods=['POST'])
def chat():
    try:
        file = request.files.get('file')
        if not file or file.filename == '':
            return jsonify({'answer': 'No file uploaded.'})

        question = request.form.get('question', '').strip()
        if not question:
            return jsonify({'answer': 'Please ask a question.'})

        history = request.form.get('history', '[]')
        import json
        history = json.loads(history)

        df, error = read_file(file)
        if error:
            return jsonify({'answer': f'Could not read file: {error}'})

        answer = answer_question(df, question, history)
        return jsonify({'answer': answer})

    except Exception as e:
        return jsonify({'answer': f'Something went wrong: {str(e)}'})
    
if __name__ == "__main__":
    print("🚀 Starting Flask server...")
    app.run(debug=True)