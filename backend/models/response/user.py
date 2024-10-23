from datetime import datetime

from server.models import *
from server.models.response.base import BaseInfo


class UserInfo(BaseInfo):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.id = kwargs.get("id", None)
        self.username = kwargs.get("username", None)
        self.avatar = kwargs.get("avatar", None)
        self.number = kwargs.get("number", None)
        self.phone = kwargs.get("phone", None)
        self.online = kwargs.get("online", None)

    @staticmethod
    def build(**kwargs):
        return vars(UserInfo(**kwargs))

    @staticmethod
    def build_from_object(user: User):
        res = UserInfo(
            id=user.id,
            username=user.username,
            avatar=user.avatar,
            number=user.number,
            phone=user.phone,
            online=user.online,
            created_at=user.created_at.strftime('%Y-%m-%d %H:%M:%S') if isinstance(user.created_at,
                                                                                   datetime) else None,
            updated_at=user.updated_at.strftime('%Y-%m-%d %H:%M:%S') if isinstance(user.updated_at,
                                                                                   datetime) else None,
            deleted_at=user.deleted_at.strftime('%Y-%m-%d %H:%M:%S') if isinstance(user.deleted_at,
                                                                                   datetime) else None,
        )
        return vars(res)
