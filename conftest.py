import requests
import pytest
from clients.api_manager import ApiManager
from utils.data_generation import DataGenerator
from Cinescope.entities.user import User
from resources.user_creds import SuperAdminCreds
from data.movies.movie_data import get_movie_payload
from constants.roles import Roles
from models.base_models import TestUser

@pytest.fixture(scope="session")
def session():
    http_session = requests.Session()
    yield http_session
    http_session.close()

@pytest.fixture(scope="session")
def api_manager(session):
    return ApiManager(session)

@pytest.fixture
def user_session():
    user_pool = []

    def _create_user_session():
        session = requests.Session()
        user_session = ApiManager(session)
        user_pool.append(user_session)
        return user_session

    yield _create_user_session

    for user in user_pool:
        user.close_session()

@pytest.fixture
def super_admin(user_session):
    new_session = user_session()

    super_admin = User(
        SuperAdminCreds.USERNAME,
        SuperAdminCreds.PASSWORD,
        [Roles.SUPER_ADMIN.value],
        new_session)

    super_admin.api.auth_api.authenticate(super_admin.creds)
    return super_admin

@pytest.fixture
def common_user(user_session, super_admin, creation_user_data):
    new_session = user_session()

    common_user = User(
        creation_user_data.email,
        creation_user_data.password,
        [Roles.USER.value],
        new_session)

    super_admin.api.user_api.create_user(creation_user_data)
    common_user.api.auth_api.authenticate(common_user.creds)
    return common_user

@pytest.fixture
def created_movie(super_admin):
    """
    Фильм создаёт SUPER_ADMIN, после теста удаляет.
    Для get/patch-тестов movies.
    """
    payload = get_movie_payload()
    movie = super_admin.api.movie_api.create_movie(payload).json()
    yield movie
    try:
        super_admin.api.movie_api.delete_movie(movie["id"], expected_status=200)
    except ValueError:
        pass

@pytest.fixture(scope="function")
def creation_user_data(test_user: TestUser) -> TestUser:
    return test_user.model_copy(update={"verified": True, "banned": False})

@pytest.fixture
def test_user() -> TestUser:
    random_password = DataGenerator.generate_random_password()

    return TestUser(
        email=DataGenerator.generate_random_email(),
        fullName=DataGenerator.generate_random_name(),
        password=random_password,
        passwordRepeat=random_password,
        roles=[Roles.USER]
    )

@pytest.fixture
def admin(user_session, super_admin, creation_user_data):
    """
    Пользователь с ролью ADMIN (не SUPER_ADMIN).
    """
    new_session = user_session()

    created = super_admin.api.user_api.create_user(creation_user_data).json()

    super_admin.api.user_api.edit_user(
        created["id"],
        {
            "roles": [Roles.ADMIN.value],
            "verified": True,
            "banned": False,
        },
    )

    admin_user = User(
        creation_user_data.email,
        creation_user_data.password,
        [Roles.ADMIN.value],
        new_session,
    )
    admin_user.api.auth_api.authenticate(admin_user.creds)
    return admin_user