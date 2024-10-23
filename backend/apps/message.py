import json
from datetime import datetime, timedelta

from flask import g
from flask_socketio import emit, send, join_room, leave_room
from sqlalchemy import desc

from server.extensions import redis_store
from server.models import Message, session, User, Group, ChatHistory, group_membership, Friend, TemporarilyBottle
from flask import request
from flask_socketio import disconnect
from server.configs.config import baseConfig
from server.models import session, User
from server.models.response.history import HistoryInfo
from server.models.response.messgae import MessageInfo
from server.models.response.user import UserInfo
from server.utils.jwt_utils import JWTUtils


def authenticate(token):
    if token:
        decoded_token = JWTUtils.decode_token(token)
        print(decoded_token)
        if 'error' in decoded_token:
            disconnect(request.sid)
        if "id" not in decoded_token:
            disconnect(request.sid)
        user_obj = session.query(User).filter_by(id=decoded_token.get('id')).first()
        if user_obj is None:
            disconnect(request.sid)
        if redis_store.get(token):
            print("sid", request.sid)
            return True
        else:
            redis_store.set(str(token), json.dumps(UserInfo.build_from_object(user_obj)),
                            ex=baseConfig.REDIS_EXPIRES_TIME)
        return True
    else:
        # 没有授权头部，断开连接
        disconnect(request.sid)
        return False


def disconnect_user(data):
    token = data['token']
    redis_store.delete(token)
    disconnect(request.sid)


def left_user(data):
    room = data['room']
    user_data = json.loads(redis_store.get(data['token']))
    leave_room(room)
    emit('status', {'msg': user_data['username'] + ' has left the room.'}, room=room)


def left_group(data):
    room = data['room']
    user_data = json.loads(redis_store.get(data['token']))
    leave_room(room)
    emit('status', {'msg': user_data['username'] + ' has left the room.'}, room=room)


def joined_user(data):
    if not authenticate(data['token']):
        disconnect(request.sid)
    sender_id = int(data['sender_id'])
    recipient_id = int(data['recipient_id'])
    print(type(sender_id), type(recipient_id))
    room = '_'.join(sorted([str(sender_id), str(recipient_id)]))
    print("user:room", room)
    try:
        session.query(User).filter_by(id=sender_id).update({"online": 1})
        session.query(User).filter_by(id=recipient_id).update({"online": 1})
        session.commit()
        message_objs = session.query(Message).filter(
            (Message.sender_id == sender_id) & (Message.recipient_id == recipient_id) | (
                    Message.sender_id == recipient_id) & (Message.recipient_id == sender_id)).order_by(
            Message.timestamp).all()
        message = [MessageInfo.build_from_object_r(i) for i in message_objs]
    finally:
        session.close()
    join_room(room)
    emit('joined_user_message', {'message': message}, room=room)


def joined_group(data):
    if not authenticate(data['token']):
        disconnect(request.sid)
    room = data['room']
    print("group:room", room)
    user_data = json.loads(redis_store.get(data['token']))
    try:
        session.query(User).filter_by(id=user_data['id']).update({"online": 1})
        session.commit()
        message_objs = session.query(Message).filter_by(group_id=room).all()
        message = [MessageInfo.build_from_object(i) for i in message_objs]
    finally:
        session.close()
    join_room(room)
    emit('joined_group_message', {'message': message}, room=room)


def joined():
    print(111)
    emit('joined_message', {'message': "ok"})


def joined_history(token):
    if not authenticate(token):
        disconnect(request.sid)
    print("joined_history", token)
    user_data = json.loads(redis_store.get(token))
    print("joined_history:user_data:", user_data)
    join_room(user_data['number'])
    print(user_data['number'])
    group_membership_objs = session.query(group_membership).filter_by(user_id=user_data['id']).all()
    group_ids = [i.group_id for i in group_membership_objs]
    histories = session.query(ChatHistory).filter(
        (ChatHistory.sender_id == user_data['id']) | (ChatHistory.recipient_id == user_data['id']) | (
            ChatHistory.group_id.in_(group_ids))).all()
    histories = [HistoryInfo.build_from_object(i) for i in histories]
    emit('joined_history_message', {'histories': histories}, room=user_data['number'])


def handle_private_message(data):
    print(data, type(redis_store))
    user_data = json.loads(redis_store.get(data['token']))
    print(user_data, type(user_data))
    room = data['room']
    recipient_id = data['recipient_id']
    content = data['content']
    image_url = data['image_url']
    audio_url = data['audio_url']
    # 在这里处理私聊消息的逻辑
    try:
        msg = Message(sender_id=user_data['id'], recipient_id=recipient_id, content=content, image_url=image_url,
                      audio_url=audio_url, created_at=datetime.utcnow())
        session.add(msg)
        session.flush()  # 可回显
        sender = session.query(User).filter_by(id=user_data['id']).first()
        recipient = session.query(User).filter_by(id=int(recipient_id)).first()
        msg.sender = sender
        msg.recipient = recipient
        print(msg.audio_url)
        new_msg = MessageInfo.build_from_object_r(msg)
        if recipient_id == user_data['id']:
            zj = session.query(ChatHistory).filter_by(sender_id=user_data['id'], recipient_id=user_data['id'])
            if zj.first() is not None:
                zj.update({"message": content, "updated_at": datetime.utcnow()})
            else:
                session.add(ChatHistory(sender_id=user_data['id'], recipient_id=recipient_id, message=content,
                                        created_at=datetime.utcnow()))
        else:
            temp = session.query(TemporarilyBottle).filter(
                (TemporarilyBottle.user_id == user_data['id']) & (TemporarilyBottle.friend_id == recipient_id) | (
                        TemporarilyBottle.user_id == recipient_id) & (TemporarilyBottle.friend_id == user_data['id']))
            print("temp.first():", temp.first())
            if temp.first() is None:
                h2 = session.query(ChatHistory).filter_by(sender_id=recipient_id, recipient_id=user_data['id'])
                if h2.first() is not None:
                    h2.delete()
                h = session.query(ChatHistory).filter_by(sender_id=user_data['id'], recipient_id=recipient_id)
                if h.first() is None:
                    session.add(ChatHistory(sender_id=user_data['id'], recipient_id=recipient_id, message=content,
                                            created_at=datetime.utcnow()))
                else:
                    h.update({"message": content, "updated_at": datetime.utcnow()})
        session.commit()
    finally:
        session.close()
    emit('user_message', {'message': new_msg}, room=room, broadcast=True)


def handle_group_message(data):
    group_id = data['group_id']
    content = data['content']
    image_url = data['image_url']
    audio_url = data['audio_url']
    # 在这里处理群聊消息的逻辑
    user_data = json.loads(redis_store.get(data['token']))
    try:
        msg = Message(sender_id=user_data['id'], group_id=int(group_id), content=content, image_url=image_url,
                      audio_url=audio_url, created_at=datetime.utcnow())  # datetime.now() - timedelta(hours=7)
        session.add(msg)
        session.flush()  # 可回显
        user = session.query(User).filter_by(id=user_data['id']).first()
        msg.sender = user
        new_msg = MessageInfo.build_from_object(msg)
        print("group new_msg", new_msg)
        h = session.query(ChatHistory).filter_by(group_id=group_id)
        if h.first() is None:
            session.add(ChatHistory(group_id=group_id, message=content, created_at=datetime.utcnow()))
        else:
            h.update({"message": content, "updated_at": datetime.utcnow()})
        session.commit()
    finally:
        session.close()
    # 发送群聊消息给群里的所有成员
    emit('group_message', {'message': new_msg}, room=group_id, broadcast=True)


def handle_history(data):
    user_data = json.loads(redis_store.get(data['token']))
    try:
        group_membership_objs = session.query(group_membership).filter_by(user_id=user_data['id']).all()
        group_ids = [i.group_id for i in group_membership_objs]
        histories = session.query(ChatHistory).filter(
            (ChatHistory.sender_id == user_data['id']) | (ChatHistory.recipient_id == user_data['id']) | (
                ChatHistory.group_id.in_(group_ids))).all()
        histories = [HistoryInfo.build_from_object(i) for i in histories]
        session.commit()
    finally:
        session.close()
    emit('history_message', {'history': histories}, room=user_data['number'])
