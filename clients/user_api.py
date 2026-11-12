from custom_requester.custom_requester import CustomRequester


class UserApi(CustomRequester):
    """
    Клиент UserController (auth-сервис).
    Все методы кроме публичных требуют Bearer.
    """

    def __init__(self, session, base_url):
        """
        :param base_url: AUTH_BASE_URL
        """
        super().__init__(session, base_url)
        self.user_endpoint = "/user"

    def get_users(self, params=None, expected_status=200, **kwargs):
        """GET /user — список пользователей."""
        return self.send_request(
            method="GET",
            endpoint=self.user_endpoint,
            params=params,
            expected_status=expected_status,
            **kwargs,
        )

    def create_user(self, user_data, expected_status=201, **kwargs):
        """POST /user — создание пользователя (SUPER_ADMIN)."""
        return self.send_request(
            method="POST",
            endpoint=self.user_endpoint,
            data=user_data,
            expected_status=expected_status,
            **kwargs,
        )

    def get_user(self, id_or_email, expected_status=200, **kwargs):
        """GET /user/{idOrEmail} — пользователь по id или email."""
        return self.send_request(
            method="GET",
            endpoint=f"{self.user_endpoint}/{id_or_email}",
            expected_status=expected_status,
            **kwargs,
        )

    def edit_user(self, user_id, user_data, expected_status=200, **kwargs):
        """PATCH /user/{id} — изменение roles/verified/banned."""
        return self.send_request(
            method="PATCH",
            endpoint=f"{self.user_endpoint}/{user_id}",
            data=user_data,
            expected_status=expected_status,
            **kwargs,
        )

    def delete_user(self, user_id, expected_status=200, **kwargs):
        """DELETE /user/{id} — удаление пользователя."""
        return self.send_request(
            method="DELETE",
            endpoint=f"{self.user_endpoint}/{user_id}",
            expected_status=expected_status,
            **kwargs,
        )