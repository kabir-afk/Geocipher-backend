import json
from django.core.cache import cache
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import random
from .models import Coordinates
from .serializers import CoordinatesSerializer
from .utils import score_exponential

@database_sync_to_async
def get_random_coordinate():
    random_index = random.randint(1, 299250)
    coords = Coordinates.objects.first()
    serializer = CoordinatesSerializer(coords)
    all_coords = serializer.data['coordinates']
    return all_coords[random_index]


class LobbyConsumer(AsyncWebsocketConsumer):
    ROOM_SIZE = 2
    ROOM_NAME_PREFIX = "game_room_"

    async def find_available_room(self):
        for i in range(1, 100):
            room_key = f"{self.ROOM_NAME_PREFIX}{i}"
            current_size = cache.get(room_key, 0)
            if current_size < self.ROOM_SIZE:
                return i
        return None

    async def connect(self):
        user = self.scope["user"]
        if user.is_anonymous:
            await self.close()
            return

        room_id = await self.find_available_room()
        self.room_name = f"{self.ROOM_NAME_PREFIX}{room_id}"

        if cache.get(self.room_name) is None:
            cache.set(self.room_name, 0)

        new_room_size = cache.incr(self.room_name)
        await self.channel_layer.group_add(self.room_name, self.channel_name)
        await self.accept()

        if new_room_size == self.ROOM_SIZE:
            coordinate = await get_random_coordinate()
            cache.set(f"{self.room_name}_coordinate", coordinate, timeout=3600)
            cache.set(f"{self.room_name}_guesses", {}, timeout=3600)  # reset guesses

            await self.channel_layer.group_send(self.room_name, {
                "type": "room_full_notification",
                "coordinate": coordinate,
            })

    async def receive(self, text_data):
        data = json.loads(text_data)
        user = self.scope["user"]

        if data.get('data', {}).get('event') == "ready":
            key = f"{self.room_name}_user_state"
            user_state = cache.get(key,{})
            user_state[user.username] = True
            cache.set(key,user_state)

            if len(user_state) >= self.ROOM_SIZE:
                coordinate = await get_random_coordinate()
                cache.set(f"{self.room_name}_coordinate", coordinate, timeout=3600)
                cache.set(f"{self.room_name}_guesses", {}, timeout=3600)
                
                cache.set(f"{self.room_name}_user_state", {}, timeout=3600)

                await self.channel_layer.group_send(self.room_name, {
                    "type": "room_full_notification",
                    "coordinate": coordinate,
                })

        elif data.get('data', {}).get('event') == "guess":
            guess = data['data']['user_location']
            actual_location = data['data']['actual_location']
            stats = score_exponential(actual_location,guess)
            merged_stats = guess | stats
            print("guess",guess)
            
            # FIXED: Use a lock-like pattern or handle the race condition
            key = f"{self.room_name}_guesses"
            guesses = cache.get(key, {})

            # Check if user already guessed (prevent duplicate submissions)
            # if user.username in guesses:
            #     await self.send(text_data=json.dumps({
            #         "event": "error",
            #         "message": "You have already submitted your guess"
            #     }))
            #     print("You have already submitted your guess")
            #     return
            
            # Add this user's guess
            guesses[user.username] = merged_stats
            cache.set(key, guesses, timeout=3600)
            
            # Send confirmation to the user
            await self.send(text_data=json.dumps({
                "event": "guess_received",
                "message": f"Guess received. Waiting for other players... ({len(guesses)}/{self.ROOM_SIZE})"
            }))
            
            # FIXED: Check against ROOM_SIZE constant, not dynamic room_size
            # This prevents issues if someone disconnects
            if len(guesses) >= self.ROOM_SIZE:
                actual_coordinate = cache.get(f"{self.room_name}_coordinate")
                
                await self.channel_layer.group_send(self.room_name, {
                    "type": "all_players_guessed",
                    "guesses": guesses,
                    "actual_coordinate": actual_coordinate,
                })

    async def all_players_guessed(self, event):
        """Triggered once all players have sent their guess."""
        await self.send(text_data=json.dumps({
            "event": "results_ready",
            "guesses": event["guesses"],
            "actual_coordinate": event.get("actual_coordinate"),
        }))

    async def room_full_notification(self, event):
        coordinate = event["coordinate"]
        await self.send(text_data=json.dumps({
            "event": "room_full",
            "coordinate": coordinate,
        }))

    async def disconnect(self, close_code):
        if cache.get(self.room_name):
            cache.decr(self.room_name)
            if cache.get(self.room_name) <= 0:
                cache.delete(self.room_name)
                cache.delete(f"{self.room_name}_coordinate")
                cache.delete(f"{self.room_name}_guesses")
        await self.channel_layer.group_discard(self.room_name, self.channel_name)