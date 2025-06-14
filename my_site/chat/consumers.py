# chat/consumers.py


import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from .models import GuestUser, Room, Message
from django.utils.timezone import now



class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        # Создаём комнату при необходимости
        self.room, _ = Room.objects.get_or_create(name=self.room_name)

        # Получаем IP
        ip_address = self.scope.get('client')[0]

        # Получаем имя пользователя из сессии или делаем "Аноним"
        session = self.scope.get('session')
        username = session.get('username', 'Аноним') if session else 'Аноним'

        # Ищем гостя по IP или создаём
        self.guest_user, _ = GuestUser.objects.get_or_create(
            ip_address=ip_address,
            defaults={
                'username': username,
                'room_name': self.room_name,
                'created_at': now()
            }
        )

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
            username_str = text_data_json.get('username', self.guest_user.username)

            # Сохраняем сообщение
            Message.objects.create(
                username=self.guest_user,
                room=self.room,
                content=message,
                timestamp=now()
            )

            # Рассылаем
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
        self.send(text_data=json.dumps({
            'type': 'chat',
            'message': event['message'],
            'username': event['username']
        }))