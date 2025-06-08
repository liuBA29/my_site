# chat/consumers.py

# chat/consumers.py

import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name,
        )

        self.accept()

        self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': f'Вы подключены к комнате: {self.room_name}'
        }))

    def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message = text_data_json['message']
            username_str = text_data_json.get('username', 'Аноним')

            # Рассылка без сохранения
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'username': username_str
                }
            )
        except Exception as e:
            print(f"[receive error] {e}")
            self.close()

    def chat_message(self, event):
        message = event['message']
        username = event['username']

        self.send(text_data=json.dumps({
            'type': 'chat',
            'message': message,
            'username': username
        }))
