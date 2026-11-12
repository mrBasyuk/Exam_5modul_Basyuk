import random
import uuid
from utils.data_generation import DataGenerator

GENRE_IDS = [7, 8, 9, 10]

def get_movie_payload(**overrides):
    payload = {
        "name": f"{DataGenerator.generate_random_name()} {uuid.uuid4().hex[:8]}",
        "imageUrl": f"https://example.com/posters/{uuid.uuid4().hex}.jpg",
        "price": random.randint(50, 1000),
        "description": DataGenerator.generate_random_name(),
        "location": random.choice(["MSK", "SPB"]),
        "published": True,
        "genreId": random.choice(GENRE_IDS),
    }
    payload.update(overrides)
    return payload

def get_update_movie_payload(**kwargs):
    allowed = ("name", "description", "price", "location", "imageUrl", "published", "genreId")
    return {k: v for k, v in kwargs.items() if k in allowed and v is not None}