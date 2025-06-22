# chat/consumers.py

import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from django.utils.timezone import now


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        from .models import GuestUser, Room
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        self.room, _ = Room.objects.get_or_create(name=self.room_name)

        session = self.scope.get('session')
        username = session.get('username', 'Аноним') if session else 'Аноним'
        ip_address = self.scope.get('client')[0]

        if self.scope['user'].is_authenticated:
            # Для авторизованного пользователя можно сохранять его Django User
            self.user = self.scope['user']
            self.guest_user = None
        else:
            # Гость по IP + сессии
            self.guest_user, _ = GuestUser.objects.get_or_create(
                ip_address=ip_address,
                defaults={
                    'username': username,
                    'room_name': self.room_name,
                    'created_at': now()
                }
            )
            # Если имя в сессии изменилось — синхронизируем:
            if self.guest_user.username != username or self.guest_user.room_name != self.room_name:
                self.guest_user.username = username
                self.guest_user.room_name = self.room_name
                self.guest_user.save()
            self.user = self.guest_user

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
        from .models import Message
        try:
            data = json.loads(text_data)
            msg = data['message']

            if self.scope['user'].is_authenticated:
                author = self.scope['user']
                # Сохраняем с user
                # Message.objects.create(
                #     user=author,
                #     room=self.room,
                #     content=msg,
                #     timestamp=now()
                # )
                username_str = author.username
            else:
                guest = self.guest_user
                # Сохраняем с guest_user
                # Message.objects.create(
                #     guest_user=guest,
                #     room=self.room,
                #     content=msg,
                #     timestamp=now()
                # )
                username_str = guest.username if guest else "Аноним"

            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': msg,
                    'username': username_str,
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
