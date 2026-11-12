import random
import string
from faker import Faker

faker = Faker()

class DataGenerator:

    @staticmethod
    def generate_random_name():
        return faker.name()

    @staticmethod
    def generate_random_email():
        return faker.email(domain="example.ru")

    @staticmethod
    def generate_random_password():
        """
        Генерирует пароль, который точно проходит валидацию Cinescope.
        """
        letters = string.ascii_letters          # a-zA-Z
        digits = string.digits                  # 0-9
        special = "?@#$%^&*_-+()[]{}><\\/|\"'.,:;"

        password_chars = [
            random.choice(letters),
            random.choice(digits),
        ]

        all_chars = letters + digits + special
        length = random.randint(10, 14)
        for _ in range(length - 2):
            password_chars.append(random.choice(all_chars))

        random.shuffle(password_chars)
        return "".join(password_chars)