from datetime import datetime

from server.models import Friend, TemporarilyBottle
from server.models.response.base import BaseInfo
from server.models.response.user import UserInfo


class FriendInfo(BaseInfo):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.id = kwargs.get("id", None)
        self.user = kwargs.get("user", {})
        self.friend = kwargs.get("friend", {})
        self.type_number = kwargs.get("type_number", None)
        self.status = kwargs.get("status", None)

    @staticmethod
    def build(**kwargs):
        return vars(FriendInfo(**kwargs))

    @staticmethod
    def build_from_object(friend: Friend):
        res = FriendInfo(
            id=friend.id,
            user=UserInfo.build_from_object(friend.user),
            friend=UserInfo.build_from_object(friend.friend),
            type_number=friend.type_number,
            status=friend.status,
            created_at=friend.created_at.strftime('%Y-%m-%d %H:%M:%S') if isinstance(friend.created_at,
                                                                                     datetime) else None,
            updated_at=friend.updated_at.strftime('%Y-%m-%d %H:%M:%S') if isinstance(friend.updated_at,
                                                                                     datetime) else None,
            deleted_at=friend.deleted_at.strftime('%Y-%m-%d %H:%M:%S') if isinstance(friend.deleted_at,
                                                                                     datetime) else None,
        )
        return vars(res)


class TemporarilyBottleInfo(BaseInfo):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.id = kwargs.get("id", None)
        self.user = kwargs.get("user", {})
        self.friend = kwargs.get("friend", {})
        self.state = kwargs.get("state", {})
        self.friend_table_id = kwargs.get("friend_table_id", None)

    @staticmethod
    def build(**kwargs):
        return vars(TemporarilyBottleInfo(**kwargs))

    @staticmethod
    def build_from_object(friend: TemporarilyBottle, id):
        res = TemporarilyBottleInfo(
            id=friend.id,
            user=UserInfo.build_from_object(friend.user),
            friend=UserInfo.build_from_object(friend.friend),
            state=friend.state,
            friend_table_id=id,
            created_at=friend.created_at.strftime('%Y-%m-%d %H:%M:%S') if isinstance(friend.created_at,
                                                                                     datetime) else None,
            updated_at=friend.updated_at.strftime('%Y-%m-%d %H:%M:%S') if isinstance(friend.updated_at,
                                                                                     datetime) else None,
            deleted_at=friend.deleted_at.strftime('%Y-%m-%d %H:%M:%S') if isinstance(friend.deleted_at,
                                                                                     datetime) else None,
        )
        return vars(res)
