import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils import timezone
from .models import Message, Room
from channels.db import database_sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        username = text_data_json['username']
        time_sent = timezone.now().strftime('%H:%M:%S %d/%m/%Y')

        # ✅ FIXED: Properly call database_sync_to_async functions
        await self.save_message(message, username, self.room_name, timezone.now())
        
        # ✅ FIXED: Mark messages as read
        await self.mark_message_as_read(self.room_name, username)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {   
                'type': 'chat_message',
                'message': message,
                'username': username,
                'time': time_sent
            }
        )

    async def chat_message(self, event):
        message = event['message']
        username = event['username']
        time = event['time']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'username': username,
            'time': time,
            'read_msg': True 
        }))

    # ✅ FIXED: Use database_sync_to_async as decorator
    @database_sync_to_async
    def save_message(self, message, username, room_name, time_sent):      
        room = Room.objects.get(name=room_name) 
        Message.objects.create(
            value=message,
            user=username,
            room=room,
            date=time_sent
        )

    # ✅ FIXED: Use database_sync_to_async as decorator
    @database_sync_to_async
    def mark_message_as_read(self, room_name, username):
        """Mark messages as read for the current user in the room."""
        try:
            room = Room.objects.get(name=room_name)
            # Mark messages as read for the other user in the room
            Message.objects.filter(room=room, read_msg=False).exclude(user=username).update(read_msg=True)
        except Room.DoesNotExist:
            print(f"Room with name {room_name} does not exist.")
        except Exception as e:
            print(f"Error in mark_message_as_read: {e}")