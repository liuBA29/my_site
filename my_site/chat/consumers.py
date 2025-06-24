# chat/consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import async_to_sync
from django.utils.timezone import now


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        from .models import GuestUser, Room

        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        print(f"[DEBUG] Подключение к комнате: {self.room_name}")


        # Присоединение к группе комнаты
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )


        await self.accept()
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': f'Вы подключились к комнате: {self.room_name}'
        }))

    async def disconnect(self, close_code):
        # Удаление из группы комнаты
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get('message')
        username = data.get('username', 'Аноним')

        # Отправка сообщения в группу
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': username,
            }
        )

    async def chat_message(self, event):
        message = event['message']
        username = event['username']

        # Отправка сообщения обратно в WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'username': username,
        }))

