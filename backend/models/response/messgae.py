from datetime import datetime

import pytz

from server.models import Group, Message
from server.models.response.base import BaseInfo
from server.models.response.group import GroupInfo
from server.models.response.user import UserInfo


class MessageInfo(BaseInfo):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.id = kwargs.get("id", None)
        self.image_url = kwargs.get("image_url", None)
        self.audio_url = kwargs.get("audio_url", None)
        self.recipient = kwargs.get("recipient", {})
        self.sender = kwargs.get("sender", {})
        self.content = kwargs.get("content", {})
        self.timestamp = kwargs.get("timestamp", {})

    @staticmethod
    def build(**kwargs):
        return vars(MessageInfo(**kwargs))

    @staticmethod
    def build_from_object(message: Message):
        res = MessageInfo(
            id=message.id,
            content=message.content,
            image_url=message.image_url,
            audio_url=message.audio_url,
            sender=UserInfo.build_from_object(message.sender),
            created_at=message.created_at.strftime('%Y-%m-%d %H:%M:%S') if isinstance(message.created_at,
                                                                                      datetime) else None,
            updated_at=message.updated_at.strftime('%Y-%m-%d %H:%M:%S') if isinstance(message.updated_at,
                                                                                      datetime) else None,
            deleted_at=message.deleted_at.strftime('%Y-%m-%d %H:%M:%S') if isinstance(message.deleted_at,
                                                                                      datetime) else None,
            timestamp=message.timestamp.strftime('%Y-%m-%d %H:%M:%S') if isinstance(message.timestamp,
                                                                                    datetime) else None,
        )
        return vars(res)

    @staticmethod
    def build_from_object_r(message: Message):
        res = MessageInfo(
            id=message.id,
            content=message.content,
            image_url=message.image_url,
            audio_url=message.audio_url,
            sender=UserInfo.build_from_object(message.sender),
            recipient=UserInfo.build_from_object(message.recipient),
            created_at=message.created_at.strftime('%Y-%m-%d %H:%M:%S') if isinstance(message.created_at,
                                                                                      datetime) else None,
            updated_at=message.updated_at.strftime('%Y-%m-%d %H:%M:%S') if isinstance(message.updated_at,
                                                                                      datetime) else None,
            deleted_at=message.deleted_at.strftime('%Y-%m-%d %H:%M:%S') if isinstance(message.deleted_at,
                                                                                      datetime) else None,
            timestamp=message.timestamp.strftime('%Y-%m-%d %H:%M:%S') if isinstance(message.timestamp,
                                                                                    datetime) else None,
        )
        return vars(res)
