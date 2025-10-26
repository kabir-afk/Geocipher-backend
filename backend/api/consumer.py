import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.cache import cache
from .models import Coordinates
from .serializers import CoordinatesSerializer
from channels.db import database_sync_to_async
import random

@database_sync_to_async
def get_random_coordinates(self):
    random_index = random.randint(1, 299250)
    coords = Coordinates.objects.first()
    serializer = CoordinatesSerializer(coords)
    all_coords = serializer.data['coordinates']
    return all_coords[random_index]

class LobbyConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        ROOM_SIZE = 2

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

        current_count = rooms[target_room]
        room_is_full = current_count >= ROOM_SIZE


        self.room_name = target_room
        await self.channel_layer.group_add(self.room_name, self.channel_name)
        await self.accept()

        await self.send(text_data=json.dumps({
            "event": "room_assignment",
            "room_name": self.room_name,
            "current_count": rooms[self.room_name]
        }))

        if room_is_full :
            coordinate = await get_random_coordinates(self)

            await self.channel_layer.group_send(self.room_name, {
                "type": "room_full_notification",
                "coordinate": coordinate ,
            })

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

    async def room_full_notification(self, event):
        coordinate = event['coordinate']
        await self.send(text_data=json.dumps({
            "event": "room_full",
            "coordinate": coordinate ,
        }))