# authentication/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

print("🔄 Loading ChatConsumer...")

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print(f"🔄 WebSocket connect attempt for: {self.scope['url_route']['kwargs']['room_name']}")
        
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        try:
            # Join room group
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            print("✅ Joined room group")

            await self.accept()
            print("✅ WebSocket connection ACCEPTED")
            
        except Exception as e:
            print(f"❌ WebSocket connect error: {e}")
            raise

    async def disconnect(self, close_code):
        print(f"🔌 WebSocket disconnected: {close_code}")
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        print(f"📨 Message received: {text_data}")
        try:
            text_data_json = json.loads(text_data)
            message = text_data_json['message']
            username = text_data_json['username']

            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {   
                    'type': 'chat_message',
                    'message': message,
                    'username': username,
                }
            )
            print("✅ Message sent to room group")
        except Exception as e:
            print(f"❌ Error processing message: {e}")

    async def chat_message(self, event):
        message = event['message']
        username = event['username']
        
        print(f"📤 Sending message to WebSocket: {message}")
        
        await self.send(text_data=json.dumps({
            'message': message,
            'username': username,
        }))

print("✅ ChatConsumer loaded successfully")