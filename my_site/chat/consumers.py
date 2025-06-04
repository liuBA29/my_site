# chat/consumers.py

import json
from channels.generic.websocket import WebsocketConsumer

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

        self.send(text_data=json.dumps({
            'type':'connection_established',
            'message':'You are now connected!'
        }))

    def receive(self, text_data):  # ✅ теперь это метод класса, а не вложенный
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        print('Message:', message)

        # можешь также обратно отправить сообщение на клиент:
        self.send(text_data=json.dumps({
            'type': 'chat',
            'message': message
        }))
