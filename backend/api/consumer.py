import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.cache import cache

class LobbyConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        ROOM_SIZE = 5

        rooms = cache.get("rooms", {})
        target_room = None
        for room, count in rooms.items():
            if count < ROOM_SIZE:
                target_room = room
                rooms[room] += 1
                break
        if not target_room:
            target_room = f"room_{len(rooms)+1}"
            rooms[target_room] = 1
        cache.set("rooms", rooms)

        self.room_name = target_room
        await self.channel_layer.group_add(self.room_name, self.channel_name)
        await self.accept()

        await self.send(text_data=json.dumps({
            "event": "room_assignment",
            "room_name": self.room_name,
            "current_count": rooms[self.room_name]
        }))

    async def disconnect(self, close_code):
        rooms = cache.get("rooms", {})
        if hasattr(self, "room_name") and self.room_name in rooms:
            rooms[self.room_name] -= 1
            if rooms[self.room_name] <= 0:
                del rooms[self.room_name]
            cache.set("rooms", rooms)
        
        # Always discard the user from the group
        await self.channel_layer.group_discard(self.room_name, self.channel_name)


    async def receive(self, text_data):
        try:
            await self.channel_layer.group_send(
                self.room_name,
                {
                    'type': 'lobby_message',
                    'message': text_data
                }
            )
        except json.JSONDecodeError:
            print(f"Invalid JSON received: {text_data}")
            await self.send(text_data=json.dumps({
                'error': 'Invalid JSON format'
            }))
    async def lobby_message(self, event):
            message = event['message']
            await self.send(message)