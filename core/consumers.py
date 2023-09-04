# consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer

class LiveUpdatesConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass  # Handle disconnection if needed

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']

        # Process the message (e.g., fetch live updates)
        # You may want to implement a background task for fetching updates.

        # Send the updated data back to the client
        await self.send(text_data=json.dumps({
            'message': message,
        }))
