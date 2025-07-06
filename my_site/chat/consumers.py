# chat/consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import async_to_sync, sync_to_async
from django.utils.timezone import now




class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        from accounts.models import CustomUser, Room
        from .models import Message

        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        print(f"[DEBUG] Подключение к комнате: {self.room_name}")

        # Присоединение к группе комнаты
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        user = self.scope["user"]

        if not user.is_authenticated:
            await self.close()
            return

        # Отправка сообщения только подключившемуся пользователю
        if user.is_superuser:
            await self.send(text_data=json.dumps({
                'type': 'connection_established',
                'message': f'Вы подключились к комнате: {self.room_name}'
            }))
        else:
            await self.send(text_data=json.dumps({
                'type': 'connection_established',
                'message': 'Вы подключились'
            }))

        # Уведомляем других участников комнаты
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_joined',
                'username': user.username,
            }
        )

        # Загружаем последние сообщения
        @sync_to_async
        def get_room_and_messages(room_slug):
            room = Room.objects.get(slug=room_slug)
            messages = list(room.messages.select_related('user').order_by('-timestamp')[:50])
            return room, messages

        room, messages = await get_room_and_messages(self.room_name)

        for message in reversed(messages):  # от старых к новым
            await self.send(text_data=json.dumps({
                'message': message.content,
                'username': message.user.username,
                'timestamp': message.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            }))

    async def disconnect(self, close_code):
        from accounts.models import CustomUser, Room
        from .models import Message

        # Удаление из группы комнаты
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):


        data = json.loads(text_data)
        message = data.get('message')
        username = data.get('username')
        room_slug = self.room_name

        from accounts.models import CustomUser, Room
        from .models import Message

        user = await sync_to_async(CustomUser.objects.get)(username=username)
        room = await sync_to_async(Room.objects.get)(slug=room_slug)

        # Сохраняем сообщение
        await sync_to_async(Message.objects.create)(
            user=user,
            room=room,
            content=message
        )

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


    async def user_joined(self, event):
        username = event['username']

        # Не отправляем подключившемуся самому
        if self.scope["user"].username != username:
            await self.send(text_data=json.dumps({
                'type': 'user_joined',
                'message': f'{username} присоединился к чату',
            }))


