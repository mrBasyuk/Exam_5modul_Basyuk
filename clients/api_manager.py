from clients.auth_api import AuthApi
from clients.user_api import UserApi
from clients.movies_api import MovieApi
from config.base_urls import BASE_URL, AUTH_BASE_URL


class ApiManager:
    def __init__(self, session):
        self.session = session
        self.auth_api = AuthApi(session, AUTH_BASE_URL)
        self.user_api = UserApi(session, AUTH_BASE_URL)
        self.movie_api = MovieApi(session, BASE_URL)

    def close_session(self):
        self.session.close()