# Exam: MovieApi + tests for /moviesgit add .

import pytest
from data.movies.movie_data import get_movie_payload, get_update_movie_payload
from utils.data_generation import DataGenerator
import uuid


@pytest.mark.api
class TestMovies:
    """
    Movies через фикстуры проекта: super_admin, common_user, created_movie.
    """
    @pytest.mark.positive
    def test_get_movies_list(self, api_manager):
        """PUBLIC: список фильмов без токена."""
        data = api_manager.movie_api.get_movies(
            params={"page": 1, "pageSize": 5}
        ).json()
        assert "movies" in data
        assert isinstance(data["movies"], list)
        assert data["pageSize"] == 5

    @pytest.mark.positive
    def test_create_movie(self, super_admin):
        """SUPER_ADMIN может создать фильм."""
        payload = get_movie_payload()
        movie = super_admin.api.movie_api.create_movie(payload).json()
        try:
            assert movie.get("id")
            assert movie["name"] == payload["name"]
            assert movie["price"] == payload["price"]
            assert movie["location"] == payload["location"]
            assert movie["genreId"] == payload["genreId"]
        finally:
            super_admin.api.movie_api.delete_movie(movie["id"])

    @pytest.mark.positive
    def test_get_movie_by_id(self, api_manager, created_movie):
        """PUBLIC: GET /movies/{id}."""
        data = api_manager.movie_api.get_movie_by_id(created_movie["id"]).json()
        assert data["id"] == created_movie["id"]
        assert data["name"] == created_movie["name"]

    @pytest.mark.positive
    def test_patch_movie(self, super_admin, created_movie):
        """SUPER_ADMIN: PATCH фильма."""
        new_name = f"{DataGenerator.generate_random_name()} {uuid.uuid4().hex[:6]}"
        updated = super_admin.api.movie_api.patch_movie(
            created_movie["id"],
            get_update_movie_payload(name=new_name),
        ).json()
        assert updated["id"] == created_movie["id"]
        assert updated["name"] == new_name

    @pytest.mark.positive
    def test_delete_movie(self, super_admin):
        """SUPER_ADMIN: DELETE → GET 404."""
        movie = super_admin.api.movie_api.create_movie(get_movie_payload()).json()
        super_admin.api.movie_api.delete_movie(movie["id"], expected_status=200)
        super_admin.api.movie_api.get_movie_by_id(movie["id"], expected_status=404)

    @pytest.mark.positive
    def test_get_movies_filter_by_location(self, super_admin):
        """Фильтр locations + createdAt=desc, чтобы новый фильм был на 1-й странице."""
        payload = get_movie_payload(location="MSK")
        movie = super_admin.api.movie_api.create_movie(payload).json()
        try:
            data = super_admin.api.movie_api.get_movies(
                params={
                    "locations": ["MSK"],
                    "page": 1,
                    "pageSize": 20,
                    "createdAt": "desc",
                }
            ).json()
            assert movie["id"] in [m["id"] for m in data["movies"]]
            for m in data["movies"]:
                assert m["location"] == "MSK"
        finally:
            super_admin.api.movie_api.delete_movie(movie["id"])



    @pytest.mark.negative
    def test_create_movie_forbidden_for_user(self, common_user):
        """
        Роль USER не имеет права на POST /movies.
        common_user уже залогинен своей session с токеном USER.
        Ожидаем 403 (если стенд вернёт 401 — поменяй expected_status).
        """
        common_user.api.movie_api.create_movie(
            get_movie_payload(),
            expected_status=403,
        )

    @pytest.mark.positive
    @pytest.mark.parametrize(
        "filter_params, create_overrides, check",
        [
            # 1) цена: все фильмы в ответе в диапазоне minPrice..maxPrice
            (
                    {"minPrice": 100, "maxPrice": 500, "page": 1, "pageSize": 20, "createdAt": "desc"},
                    {"price": 250},
                    "price_range",
            ),
            # 2) локация
            (
                    {"locations": ["MSK"], "page": 1, "pageSize": 20, "createdAt": "desc"},
                    {"location": "MSK"},
                    "location",
            ),
            (
                    {"locations": ["SPB"], "page": 1, "pageSize": 20, "createdAt": "desc"},
                    {"location": "SPB"},
                    "location",
            ),
            # 3) genreId
            (
                    {"genreId": 7, "page": 1, "pageSize": 20, "createdAt": "desc"},
                    {"genreId": 7},
                    "genreId",
            ),
            (
                    {"genreId": 8, "page": 1, "pageSize": 20, "createdAt": "desc"},
                    {"genreId": 8},
                    "genreId",
            ),
        ],
        ids=[
            "filter_by_price_range",
            "filter_by_location_MSK",
            "filter_by_location_SPB",
            "filter_by_genreId_7",
            "filter_by_genreId_8",
        ],
    )
    def test_get_movies_by_filter(
            self, super_admin, filter_params, create_overrides, check
    ):
        """
        GET /movies с фильтрами (parametrize).

        Создаём фильм под конкретный фильтр, запрашиваем список с createdAt=desc,
        проверяем:
        - наш id есть в выдаче;
        - все элементы ответа соответствуют фильтру.
        """
        payload = get_movie_payload(**create_overrides)
        movie = super_admin.api.movie_api.create_movie(payload).json()
        movie_id = movie["id"]

        try:
            data = super_admin.api.movie_api.get_movies(params=filter_params).json()
            movies = data["movies"]

            assert len(movies) >= 1, "Ожидали хотя бы один фильм по фильтру"
            assert movie_id in [m["id"] for m in movies], (
                f"Созданный фильм {movie_id} не найден в выдаче фильтра {filter_params}"
            )

            if check == "price_range":
                min_p = filter_params["minPrice"]
                max_p = filter_params["maxPrice"]
                for m in movies:
                    assert min_p <= m["price"] <= max_p, (
                        f"price={m['price']} вне диапазона [{min_p}, {max_p}]"
                    )

            elif check == "location":
                expected = create_overrides["location"]
                for m in movies:
                    assert m["location"] == expected, (
                        f"location={m['location']}, ожидалось {expected}"
                    )

            elif check == "genreId":
                expected = create_overrides["genreId"]
                for m in movies:
                    assert m["genreId"] == expected, (
                        f"genreId={m['genreId']}, ожидалось {expected}"
                    )

        finally:
            super_admin.api.movie_api.delete_movie(movie_id, expected_status=200)

    @pytest.mark.parametrize(
        "actor_fixture, expected_status",
        [
            ("super_admin", 200),  # только SUPER_ADMIN может удалять
            ("admin", 403),  # ADMIN — запрещено
            ("common_user", 403),  # USER — запрещено
        ],
        ids=["super_admin_can_delete", "admin_forbidden", "user_forbidden"],
    )
    def test_delete_movie_by_role(
            self, request, super_admin, actor_fixture, expected_status
    ):
        """
        DELETE /movies/{id} с ролевой моделью.

        Фильм всегда создаёт SUPER_ADMIN (иначе USER/ADMIN не смогут
        даже подготовить данные). Удаление выполняет actor с разным expected_status.
        """
        movie = super_admin.api.movie_api.create_movie(get_movie_payload()).json()
        movie_id = movie["id"]

        actor = request.getfixturevalue(actor_fixture)

        try:
            actor.api.movie_api.delete_movie(movie_id, expected_status=expected_status)
            if expected_status == 200:
                super_admin.api.movie_api.get_movie_by_id(movie_id, expected_status=404)
            else:
                super_admin.api.movie_api.delete_movie(movie_id, expected_status=200)
        except Exception:
            try:
                super_admin.api.movie_api.delete_movie(movie_id, expected_status=200)
            except ValueError:
                pass
            raise