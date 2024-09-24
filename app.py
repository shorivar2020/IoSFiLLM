from flask import Flask, request, jsonify
from flask_cors import CORS
import ai

app = Flask(__name__)
CORS(app)  # Разрешаем запросы с другого домена (фронтенд)


@app.route('/api/check', methods=['POST'])
def check_question():
    data = request.json  # Получаем JSON данные из запроса
    question = data.get('question', '').lower()  # Получаем вопрос и приводим к нижнему регистру
    answer = ai(question)
    return jsonify({"answer": answer})


if __name__ == '__main__':
    app.run(debug=True)
