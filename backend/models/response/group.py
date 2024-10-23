from datetime import datetime

from server.models import Group
from server.models.response.base import BaseInfo


class GroupInfo(BaseInfo):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.id = kwargs.get("id", None)
        self.name = kwargs.get("name", None)
        self.members = kwargs.get("members", [])
        self.owner = kwargs.get("owner", None)
        self.avatar = kwargs.get("avatar", None)

    @staticmethod
    def build(**kwargs):
        return vars(GroupInfo(**kwargs))

    @staticmethod
    def build_from_object(group: Group):
        res = GroupInfo(
            id=group.id,
            name=group.name,
            owner=group.owner.number,
            avatar=group.avatar,
            members=[{"username": i.username, "avatar": i.avatar, "online": i.online, "number": i.number}
                     for i in group.members],
            created_at=group.created_at.strftime('%Y-%m-%d %H:%M:%S') if isinstance(group.created_at,
                                                                                    datetime) else None,
            updated_at=group.updated_at.strftime('%Y-%m-%d %H:%M:%S') if isinstance(group.updated_at,
                                                                                    datetime) else None,
            deleted_at=group.deleted_at.strftime('%Y-%m-%d %H:%M:%S') if isinstance(group.deleted_at,
                                                                                    datetime) else None,
        )
        return vars(res)
