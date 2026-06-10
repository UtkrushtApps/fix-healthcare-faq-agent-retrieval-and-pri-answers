from flask import Flask, request, jsonify
from app.agent import run_agent

app = Flask(__name__)


@app.route('/assistant/ask', methods=['POST'])
def ask():
    data = request.get_json(force=True)
    query = data.get('query', '').strip()
    patient_email = data.get('patient_email', '')

    if not query:
        return jsonify({'error': 'query is required'}), 400

    result = run_agent(query, patient_email=patient_email)
    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True)
