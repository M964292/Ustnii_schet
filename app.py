import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template, request, jsonify, session
from datetime import datetime
import time
import random
import requests
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Telegram setup
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = "Mufassa_n1"  # Ваш Telegram username или chat_id

def send_to_telegram(name, number, time_taken, errors):
    try:
        message = f"""
🏆 Результаты турнира по устному счету:

👤 Участник: {name}
🔢 Число: {number}
⏱ Время: {time_taken} сек
❌ Ошибок: {errors}

📅 {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}
"""
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "HTML"
        }
        response = requests.post(url, data=data)
        return response.status_code == 200
    except Exception as e:
        print(f"Error sending to Telegram: {e}")
        return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start', methods=['POST'])
def start():
    name = request.form.get('name')
    if not name:
        return jsonify({'error': 'Введите имя'}), 400
    
    # Генерируем случайное число от 1 до 1000
    number = random.randint(1, 1000)
    
    session['name'] = name
    session['number'] = number
    session['start_time'] = time.time()
    session['errors'] = 0
    
    return jsonify({
        'success': True,
        'number': number
    })

@app.route('/submit', methods=['POST'])
def submit():
    if 'name' not in session:
        return jsonify({'error': 'Не авторизован'}), 401
    
    name = session['name']
    number = session['number']
    time_taken = round(time.time() - session['start_time'], 2)
    errors = session['errors']
    
    success = send_to_telegram(name, number, time_taken, errors)
    
    if success:
        session.clear()
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Ошибка отправки результатов'}), 500

@app.route('/record_error', methods=['POST'])
def record_error():
    if 'name' not in session:
        return jsonify({'error': 'Не авторизован'}), 401
    
    session['errors'] = session.get('errors', 0) + 1
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True)
