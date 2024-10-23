import random
import string
from datetime import datetime, timedelta
from sqlalchemy import String, ForeignKey, Table
from sqlalchemy import create_engine, Column, DateTime, Integer, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, scoped_session, backref
from sqlalchemy.orm import sessionmaker
from werkzeug.security import generate_password_hash, check_password_hash

from server.configs.config import DatabaseConfig

engine = create_engine(
    url=DatabaseConfig.URL,
    max_overflow=DatabaseConfig.MAX_OVERFLOW,
    pool_size=DatabaseConfig.POOL_SIZE,
    pool_timeout=DatabaseConfig.POOL_TIMEOUT,
    pool_recycle=DatabaseConfig.POOLRECYCLE,
)

Base = declarative_base()
Session = sessionmaker(bind=engine)
session = scoped_session(Session)  # 创建线程安全的session 对象


class BaseModel(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = Column(DateTime, nullable=True)


# 用户模型
class User(BaseModel):
    __tablename__ = 'users'
    username = Column(String(64), unique=True, nullable=False)
    number = Column(String(255))
    avatar = Column(String(255), nullable=True,
                    default="https://img.zcool.cn/community/01cfd95d145660a8012051cdb52093.png@1280w_1l_2o_100sh.png")
    phone = Column(String(11), unique=True, nullable=True)
    password_hash = Column(String(128), nullable=False)
    online = Column(Integer, default=0)  # 0离线,1在线,2繁忙
    latitude = Column(String(255), comment="纬度")
    longitude = Column(String(255), comment="经度")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.number = self.generate_random_number()
        self.latitude = self.generate_random_latitude()
        self.longitude = self.generate_random_longitude()

    @staticmethod
    def generate_random_number():
        return ''.join([random.choice(string.digits) if i != 0 else random.choice(string.digits[1:]) for i in range(8)])

    @staticmethod
    def generate_random_latitude():
        return str(round(random.uniform(-90, 90), 6))

    @staticmethod
    def generate_random_longitude():
        return str(round(random.uniform(-180, 180), 6))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_online(self):
        return self.online


# 好友模型
class Friend(BaseModel):
    __tablename__ = 'friends'

    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    friend_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    type_number = Column(Integer, default=0)  # 0:普通好友1:漂流瓶好友
    status = Column(Integer, default=0)  # 是否同意 0:默认1:同意2:拒绝
    state = Column(Boolean, default=False)
    user = relationship('User', foreign_keys=[user_id], backref=backref('friend_user'))
    friend = relationship('User', foreign_keys=[friend_id], backref=backref('friend_friend'))


# 消息模型
class Message(BaseModel):
    __tablename__ = 'messages'

    sender_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    recipient_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=True)
    group_id = Column(Integer, ForeignKey('groups.id'))
    content = Column(String(256), nullable=False)
    image_url = Column(String(100), nullable=True)  # 图片文件名
    audio_url = Column(String(100), nullable=True)  # 音频消息的 URL
    timestamp = Column(DateTime, default=datetime.utcnow)
    sender = relationship('User', foreign_keys=[sender_id],
                          backref=backref('sent_messages'))
    recipient = relationship('User', foreign_keys=[recipient_id],
                             backref=backref('received_messages'))
    group = relationship('Group')


# 消息记录模型
class ChatHistory(BaseModel):
    __tablename__ = 'chat_history'
    sender_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=True)
    group_id = Column(Integer, ForeignKey('groups.id', ondelete='CASCADE'), nullable=True)
    recipient_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=True)
    message_count = Column(Integer, default=0)
    message = Column(String(255))
    sender = relationship('User', foreign_keys=[sender_id],
                          )
    recipient = relationship('User', foreign_keys=[recipient_id],
                             )
    group = relationship('Group')


# 群组模型
class Group(BaseModel):
    __tablename__ = 'groups'
    name = Column(String(64), nullable=False)
    number = Column(String(255))
    members = relationship('User', secondary='group_membership', backref='groups')
    owner_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    owner = relationship('User', foreign_keys=[owner_id],
                         backref=backref('group_owner'))
    avatar = Column(String(255), nullable=True,
                    default="https://img1.baidu.com/it/u=2472550237,3508413336&fm=253&fmt=auto&app=138&f=JPEG?w=400&h=400")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.number = self.generate_random_number()

    @staticmethod
    def generate_random_number():
        return "".join([random.choice(string.digits) if i != 0 else random.choice(string.digits[1:]) for i in range(8)])


# 群组用户关系表
group_membership = Table('group_membership', Base.metadata,
                         Column('user_id', Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
                         Column('group_id', Integer, ForeignKey('groups.id', ondelete='CASCADE'), primary_key=True),
                         )


# 朋友圈模型
class Article(BaseModel):
    __tablename__ = 'article'

    sender_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    content = Column(String(256), nullable=False)
    image_url = Column(String(500), nullable=True)  # 图片文件名
    video_url = Column(String(100), nullable=True)  # 视频文件名
    sender = relationship('User', foreign_keys=[sender_id])


# 点赞模型
class ArticleLike(BaseModel):
    __tablename__ = 'article_like'

    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    article_id = Column(Integer, ForeignKey('article.id', ondelete='CASCADE'), nullable=False)
    user = relationship('User', foreign_keys=[user_id])
    article = relationship('Article', foreign_keys=[article_id])


# 评论模型
class Comment(BaseModel):
    __tablename__ = 'comment'
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    article_id = Column(Integer, ForeignKey('article.id', ondelete='CASCADE'), nullable=False)
    content = Column(String(256), nullable=False)
    user = relationship('User', foreign_keys=[user_id])
    article = relationship('Article', foreign_keys=[article_id])


class TemporarilyBottle(BaseModel):
    __tablename__ = 'temporarily_bottle'

    distance = Column(String(255))
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    friend_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    user = relationship('User', foreign_keys=[user_id])
    friend = relationship('User', foreign_keys=[friend_id])
    state = Column(Boolean, default=False)


# 创建表格
def init_db():
    Base.metadata.create_all(engine)


def delete_all():
    Base.metadata.drop_all(engine)


init_db()

# delete_all()
