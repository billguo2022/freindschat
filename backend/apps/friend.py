import json

from flask import g, Blueprint, request
from sqlalchemy import exc

from server.configs.config import baseConfig
from server.extensions import redis_store
from server.models import *
from server.models.response.friend import FriendInfo
from server.models.response.res import *
from server.models.response.user import UserInfo

friend = Blueprint("friend", __name__, url_prefix="/friend")


# 我的好友
@friend.route('/get', methods=['GET'])
def get_all_friend():
    try:
        jwt_user_id = g.user.id
        key = f'friends:{jwt_user_id}'
        if redis_store.get(key):
            friends = json.loads(redis_store.get(key))
        else:
            friends = session.query(Friend).filter_by(user_id=jwt_user_id, status=1).all()
            friends_ids = [i.friend_id for i in friends]
            my_friends = session.query(User).filter(User.id.in_(friends_ids)).all()
            friends = [UserInfo.build_from_object(i) for i in my_friends]
            # redis_store.set(key, json.dumps(friends), ex=baseConfig.REDIS_EXPIRES_TIME)
    except exc.IntegrityError:
        session.rollback()
        return fail()
    except Exception as e:
        session.rollback()
        print(type(e))
        return failWithMessage(str(e))
    finally:
        session.close()
    return okWithData({"friends": friends})


# 搜索好友
@friend.route('/select', methods=['POST'])
def get_a_friend():
    if request.method == "POST":
        data = request.get_json()
        print(data)
        try:
            jwt_user_id = g.user.id
            if data['kw']:
                user = session.query(User).filter((User.number == data.get('kw')) |
                                                  (User.username == data.get('kw')) |
                                                  (User.phone == data.get('kw'))).first()
            else:
                return failWithMessage("parameter error ")
            if user is None:
                return failWithMessage("There is no such user")
            if user.id == jwt_user_id:
                return failWithMessage("own")
            friend = session.query(Friend).filter_by(user_id=jwt_user_id, friend_id=user.id).first()
            if friend:
                return failWithMessage("It's a friend")
            userObj = UserInfo.build_from_object(user)
        except exc.IntegrityError:
            session.rollback()
            return fail()
        except Exception as e:
            session.rollback()
            print(type(e))
            return failWithMessage(str(e))
        finally:
            session.close()
        return okWithData(userObj)


# 添加好友
@friend.route('/post', methods=['POST'])
def create_a_friend():
    if request.method == "POST":
        data = request.get_json()
        print(data)
        if data.get('id') is None:
            return failWithMessage("parameter error ")
        try:
            jwt_user_id = g.user.id
            key = f'friends:{jwt_user_id}'
            user = session.query(User).filter_by(id=data.get('id')).first()
            if user is None:
                return failWithMessage("There is no such user")
            friend = session.query(Friend).filter_by(user_id=jwt_user_id, friend_id=user.id).first()
            if friend:
                return failWithMessage("是好友")
            if user.id == jwt_user_id:
                return failWithMessage("own")
            else:
                session.add(Friend(user_id=jwt_user_id, friend_id=user.id, state=True))
                session.add(Friend(user_id=user.id, friend_id=jwt_user_id))
                session.commit()
                friends = session.query(Friend).filter_by(user_id=jwt_user_id, status=1).all()
                friends_ids = [i.friend_id for i in friends]
                my_friends = session.query(User).filter(User.id.in_(friends_ids)).all()
                friends = [UserInfo.build_from_object(i) for i in my_friends]
                # redis_store.set(key, json.dumps(friends), ex=baseConfig.REDIS_EXPIRES_TIME)
        except exc.IntegrityError:
            session.rollback()
            return fail()
        except Exception as e:
            session.rollback()
            print(type(e))
            return failWithMessage(str(e))
        finally:
            session.close()
        return ok()


# 删除好友
@friend.route('/delete', methods=['DELETE'])
def delete_a_friend():
    if request.method == "DELETE":
        data = request.get_json()
        print(data)
        if data.get('id') is None:
            return failWithMessage("parameter error ")
        try:
            jwt_user_id = g.user.id
            user = session.query(User).filter_by(id=data.get('id')).first()
            if user is None:
                return failWithMessage("There is no such user")
            if user.id == jwt_user_id:
                return failWithMessage("own")
            friend = session.query(Friend).filter_by(user_id=jwt_user_id, friend_id=user.id)
            if friend.first() is None:
                return failWithMessage("There is no such friend")
            friend.delete()
            friend1 = session.query(Friend).filter_by(user_id=user.id, friend_id=jwt_user_id)
            if friend1.first() is None:
                return failWithMessage("There is no such friend")
            friend1.delete()
            key = f'friends:{jwt_user_id}'
            friends = session.query(Friend).filter_by(user_id=jwt_user_id, status=1).all()
            friends_ids = [i.friend_id for i in friends]
            my_friends = session.query(User).filter(User.id.in_(friends_ids)).all()
            friends = [UserInfo.build_from_object(i) for i in my_friends]
            # redis_store.set(key, json.dumps(friends), ex=baseConfig.REDIS_EXPIRES_TIME)

            user_id = data.get('id')
            key1 = f'friends:{user_id}'
            friends1 = session.query(Friend).filter_by(user_id=user_id, status=1).all()
            friends_ids1 = [i.friend_id for i in friends1]
            my_friends1 = session.query(User).filter(User.id.in_(friends_ids1)).all()
            friends1 = [UserInfo.build_from_object(i) for i in my_friends1]
            # redis_store.set(key1, json.dumps(friends1), ex=baseConfig.REDIS_EXPIRES_TIME)
            session.query(ChatHistory).filter(
                (ChatHistory.sender_id == jwt_user_id) & (ChatHistory.recipient_id == user.id) | (ChatHistory.sender_id == user.id) & (ChatHistory.recipient_id == jwt_user_id)).delete()

            session.query(Message).filter(
                (Message.sender_id == jwt_user_id) & (Message.recipient_id == user.id) | (
                            Message.sender_id == user.id) & (Message.recipient_id == jwt_user_id)).delete()

            session.commit()
        except exc.IntegrityError:
            session.rollback()
            return fail()
        except Exception as e:
            session.rollback()
            print(type(e))
            return failWithMessage(str(e))
        finally:
            session.close()
        return ok()


# 同意好友
@friend.route('/agree', methods=['GET', 'POST'])
def agree_a_friend():
    jwt_user_id = g.user.id
    if request.method == "POST":
        data = request.get_json()
        print(data)
        if data.get('id') is None:
            return failWithMessage("parameter error ")
        try:
            friend = session.query(Friend).filter_by(id=data.get('id'))
            session.query(Friend).filter_by(user_id=friend.first().friend_id, friend_id=friend.first().user_id).update(
                {"status": 1})
            friend.update({"status": 1})
            session.query(TemporarilyBottle).filter_by(user_id=friend.first().user_id,
                                                       friend_id=friend.first().friend_id).delete()
            session.commit()

            key = f'friends:{jwt_user_id}'
            print(jwt_user_id)
            friends = session.query(Friend).filter_by(user_id=jwt_user_id, status=1).all()
            friends_ids = [i.friend_id for i in friends]
            my_friends = session.query(User).filter(User.id.in_(friends_ids)).all()
            friends = [UserInfo.build_from_object(i) for i in my_friends]
            # redis_store.set(key, json.dumps(friends), ex=baseConfig.REDIS_EXPIRES_TIME)

            print(friend.first().user_id)
            key1 = f'friends:{friend.first().user_id}'
            friends1 = session.query(Friend).filter_by(user_id=friend.first().user_id).all()
            friends_ids1 = [i.friend_id for i in friends1]
            my_friends1 = session.query(User).filter(User.id.in_(friends_ids1)).all()
            friends1 = [UserInfo.build_from_object(i) for i in my_friends1]
            # redis_store.set(key1, json.dumps(friends1), ex=baseConfig.REDIS_EXPIRES_TIME)
        except exc.IntegrityError:
            session.rollback()
            return fail()
        except Exception as e:
            session.rollback()
            print(type(e))
            return failWithMessage(str(e))
        finally:
            session.close()
        return ok()
    not_friends = session.query(Friend).filter_by(status=0, friend_id=jwt_user_id, state=True, type_number=0).all()
    return okWithData({"not_friends": [FriendInfo.build_from_object(i) for i in not_friends]})


# 拒绝好友
@friend.route('/refuse', methods=['GET', 'POST'])
def refuse_a_friend():
    if request.method == "POST":
        data = request.get_json()
        print(data)
        if data.get('id') is None:
            return failWithMessage("parameter error ")
        try:
            friend = session.query(Friend).filter_by(id=data.get('id'))
            session.query(Friend).filter_by(user_id=friend.first().friend_id, friend_id=friend.first().user_id).update(
                {"status": 2})
            friend.update({"status": 2})
            session.query(TemporarilyBottle).filter_by(user_id=friend.first().user_id,
                                                       friend_id=friend.first().friend_id).delete()
            session.commit()

        except exc.IntegrityError:
            session.rollback()
            return fail()
        except Exception as e:
            session.rollback()
            print(type(e))
            return failWithMessage(str(e))
        finally:
            session.close()
        return ok()


# 拒绝临时好友
@friend.route('/refuse/tem', methods=['GET', 'POST'])
def refuse_a_tem_friend():
    if request.method == "POST":
        data = request.get_json()
        print(data)
        if data.get('id') is None:
            return failWithMessage("parameter error ")
        try:
            session.query(TemporarilyBottle).filter_by(id=data.get('id')).delete()
            session.commit()
        except exc.IntegrityError:
            session.rollback()
            return fail()
        except Exception as e:
            session.rollback()
            print(type(e))
            return failWithMessage(str(e))
        finally:
            session.close()
        return ok()
