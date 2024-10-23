from datetime import datetime

from server.models import Group, ChatHistory
from server.models.response.base import BaseInfo
from server.models.response.group import GroupInfo
from server.models.response.user import UserInfo


class HistoryInfo(BaseInfo):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.id = kwargs.get("id", None)
        self.group = kwargs.get("group", {})
        self.recipient = kwargs.get("recipient", {})
        self.sender = kwargs.get("sender", {})
        self.message = kwargs.get("message", {})

    @staticmethod
    def build(**kwargs):
        return vars(HistoryInfo(**kwargs))

    @staticmethod
    def build_from_object(h: ChatHistory):
        res = HistoryInfo(
            id=h.id,
            message=h.message,
            group=GroupInfo.build_from_object(h.group) if h.group else None,
            sender=UserInfo.build_from_object(h.sender) if h.sender else None,
            recipient=UserInfo.build_from_object(h.recipient) if h.recipient else None,
            created_at=h.created_at.strftime('%Y-%m-%d %H:%M:%S') if isinstance(h.created_at,
                                                                                datetime) else None,
            updated_at=h.updated_at.strftime('%Y-%m-%d %H:%M:%S') if isinstance(h.updated_at,
                                                                                datetime) else None,
            deleted_at=h.deleted_at.strftime('%Y-%m-%d %H:%M:%S') if isinstance(h.deleted_at,
                                                                                datetime) else None,
        )
        return vars(res)
