from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from gevent import monkey

monkey.patch_all()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app,
                    cors_allowed_origins="*",
                    async_mode='gevent',
                    ping_timeout=60,
                    ping_interval=25)

lora_settings = {"sf": 12, "tx": 17, "bw": 125.0}
mobile_clients = set()
desktop_clients = set()

@socketio.on('connect')
def handle_connect():
    print('Новое подключение')

@socketio.on('register_mobile')
def handle_mobile_register():
    print('Мобильный клиент подключен')
    mobile_clients.add(request.sid)
    # Отправляем текущие настройки при подключении
    emit('settings_update', {"settings": lora_settings, "distance": None})

@socketio.on('register_desktop')
def handle_desktop_register():
    print('Компьютерный клиент подключен')
    desktop_clients.add(request.sid)
    # Отправляем текущие настройки при подключении
    emit('settings_update', {"settings": lora_settings, "distance": None})

@socketio.on('disconnect')
def handle_disconnect():
    sid = request.sid
    if sid in mobile_clients:
        mobile_clients.remove(sid)
        print('Мобильный клиент отключен')
    if sid in desktop_clients:
        desktop_clients.remove(sid)
        print('Компьютерный клиент отключен')

@socketio.on('mobile_update')
def handle_mobile_update(data):
    print('Получено обновление от мобильного клиента:', data)
    
    message = {
        "distance": data.get('distance'),
        "settings": data.get('settings')
    }
    
    if message["settings"]:
        global lora_settings
        lora_settings = message["settings"]
    
    for desktop_sid in desktop_clients:
        emit('message', message, room=desktop_sid)

if __name__ == "__main__":
    print("Запуск сервера на 0.0.0.0:8080")
    print("Внешний доступ через порт 80")
    socketio.run(app, host="0.0.0.0", port=8080, debug=True, log_output=True)
