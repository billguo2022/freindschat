from datetime import datetime

from typing import List

from server.models import Article, User, ArticleLike, Comment
from server.models.response.base import BaseInfo
from server.models.response.user import UserInfo


class ArticleInfo(BaseInfo):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.id = kwargs.get("id", None)
        self.sender_id = kwargs.get("sender_id", None)
        self.image_url = kwargs.get("image_url", None)
        self.video_url = kwargs.get("video_url", None)
        self.content = kwargs.get("content", None)
        self.user = kwargs.get("user", None)
        self.like = kwargs.get("like", [])
        self.comment = kwargs.get("comment", [])

    @staticmethod
    def build(**kwargs):
        return vars(ArticleInfo(**kwargs))

    @staticmethod
    def build_from_object(article: Article, likes: List[ArticleLike], comments: List[Comment]):
        res = ArticleInfo(
            id=article.id,
            sender_id=article.sender_id,
            content=article.content,
            image_url=article.image_url,
            video_url=article.video_url,
            like=[LikeInfo.build_from_object(i) for i in likes],
            comment=[CommentInfo.build_from_object(i) for i in comments],
            created_at=article.created_at.strftime('%Y-%m-%d %H:%M:%S') if isinstance(article.created_at,
                                                                                      datetime) else None,
            updated_at=article.updated_at.strftime('%Y-%m-%d %H:%M:%S') if isinstance(article.updated_at,
                                                                                      datetime) else None,
            deleted_at=article.deleted_at.strftime('%Y-%m-%d %H:%M:%S') if isinstance(article.deleted_at,
                                                                                      datetime) else None,
            user=UserInfo.build_from_object(
                User(username=article.sender.username, avatar=article.sender.avatar, online=article.sender.online,
                     number=article.sender.number, id=article.sender.id))
        )
        return vars(res)


class LikeInfo(BaseInfo):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.id = kwargs.get("id", None)
        self.user = kwargs.get("user", None)
        self.article_id = kwargs.get("article_id", None)

    @staticmethod
    def build(**kwargs):
        return vars(LikeInfo(**kwargs))

    @staticmethod
    def build_from_object(like: ArticleLike):
        res = LikeInfo(
            id=like.id,
            article_id=like.article_id,
            created_at=like.created_at.strftime('%Y-%m-%d %H:%M:%S') if isinstance(like.created_at,
                                                                                   datetime) else None,
            updated_at=like.updated_at.strftime('%Y-%m-%d %H:%M:%S') if isinstance(like.updated_at,
                                                                                   datetime) else None,
            deleted_at=like.deleted_at.strftime('%Y-%m-%d %H:%M:%S') if isinstance(like.deleted_at,
                                                                                   datetime) else None,
            user=UserInfo.build_from_object(
                User(username=like.user.username, avatar=like.user.avatar, online=like.user.online,
                     number=like.user.number, id=like.user.id))
        )
        return vars(res)


class CommentInfo(BaseInfo):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.id = kwargs.get("id", None)
        self.user = kwargs.get("user", None)
        self.content = kwargs.get("content", None)
        self.article_id = kwargs.get("article_id", None)

    @staticmethod
    def build(**kwargs):
        return vars(CommentInfo(**kwargs))

    @staticmethod
    def build_from_object(comment: Comment):
        res = CommentInfo(
            id=comment.id,
            article_id=comment.article_id,
            created_at=comment.created_at.strftime('%Y-%m-%d %H:%M:%S') if isinstance(comment.created_at,
                                                                                      datetime) else None,
            updated_at=comment.updated_at.strftime('%Y-%m-%d %H:%M:%S') if isinstance(comment.updated_at,
                                                                                      datetime) else None,
            deleted_at=comment.deleted_at.strftime('%Y-%m-%d %H:%M:%S') if isinstance(comment.deleted_at,
                                                                                      datetime) else None,
            user=UserInfo.build_from_object(
                User(username=comment.user.username, avatar=comment.user.avatar, online=comment.user.online,
                     number=comment.user.number, id=comment.user.id)),
            content=comment.content

        )
        return vars(res)
