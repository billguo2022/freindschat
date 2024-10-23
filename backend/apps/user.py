import json

from flask import g, Blueprint, request
from haversine import haversine
from sqlalchemy import exc
from server.configs.config import baseConfig
from server.extensions import redis_store
from server.models import *
from server.models.response.res import *
from server.models.response.user import UserInfo
from server.utils.jwt_utils import JWTUtils

user = Blueprint("user", __name__, url_prefix="/user")


# 根据用户距离推荐
@user.route('/recom', methods=['GET'])
def recom_user():
    try:
        jwt_user_id = g.get('user').id
        target_user = session.query(User).filter_by(id=jwt_user_id).first()
        friends = session.query(Friend).filter_by(user_id=g.get('user').id).all()
        friend_ids = [i.friend_id for i in friends]
        not_my_friends = session.query(User).filter((~User.id.in_(friend_ids)) & (User.id != jwt_user_id)).all()
        target_location = (float(target_user.latitude), float(target_user.longitude))
        closest_users = []
        min_distances = []

        for user in not_my_friends:
            if not all([user.latitude, user.longitude]):
                continue
            user_location = (float(user.latitude), float(user.longitude))
            distance = haversine(target_location, user_location)
            if len(closest_users) < 5:
                closest_users.append(user)
                min_distances.append(distance)
            else:
                max_distance = max(min_distances)
                if distance < max_distance:
                    max_index = min_distances.index(max_distance)
                    closest_users[max_index] = user
                    min_distances[max_index] = distance

        users = [UserInfo.build_from_object(i) for i in closest_users]
    except exc.IntegrityError:
        session.rollback()
        return fail()
    except Exception as e:
        session.rollback()
        print(type(e))
        return failWithMessage(str(e))
    return okWithData({"users": users})


@user.route('/userinfo/id', methods=['POST'])
def userinfo_user_id():
    if request.method == "POST":
        data = request.get_json()
        print(data)
        try:
            user = session.query(User).filter_by(id=data.get('id')).first()
        except exc.IntegrityError:
            session.rollback()
            return fail()
        except Exception as e:
            session.rollback()
            print(type(e))
            return failWithMessage(str(e))
        return okWithData(UserInfo.build_from_object(user))


@user.route('/put', methods=['PUT'])
def put_user():
    if request.method == "PUT":
        data = request.get_json()
        print(data)
        if len(data.get('phone')) > 11:
            return failWithMessage("Mobile phone number with 11 digits")
        try:
            session.query(User).filter_by(id=g.get('user').id).update(
                {"phone": data.get('phone'), "online": data.get('online')})
            user = session.query(User).filter_by(id=g.get('user').id).first()
            user = UserInfo.build_from_object(user)
            session.commit()
        except exc.IntegrityError:
            session.rollback()
            return fail()
        except Exception as e:
            session.rollback()
            print(type(e))
            return failWithMessage(str(e))
        return okWithData({"user": user})


@user.route('/location', methods=['PUT'])
def put_user_location():
    if request.method == "PUT":
        data = request.get_json()
        print(data)
        try:
            session.query(User).filter_by(id=g.get('user').id).update(
                {"latitude": data.get('latitude'), "longitude": data.get('longitude')})
            user = session.query(User).filter_by(id=g.get('user').id).first()
            user = UserInfo.build_from_object(user)
            session.commit()
        except exc.IntegrityError:
            session.rollback()
            return fail()
        except Exception as e:
            session.rollback()
            print(type(e))
            return failWithMessage(str(e))
        return okWithData({"user": user})


@user.route('/register', methods=['POST'])
def register():
    if request.method == "POST":
        data = request.get_json()
        print(data)
        if not all([data.get('username'), data.get('password'), data.get('phone')]):
            return failWithMessage("The user name, password, and mobile number cannot be empty")
        if len(data.get('username')) < 6 or len(data.get('password')) < 6:
            return failWithMessage("The user name or password contains less than 6 characters")
        user_model = User(
            username=data['username'], phone=data['phone']
        )
        user_model.set_password(password=data['password'])
        try:
            session.add(user_model)
            session.commit()
        except exc.IntegrityError:
            session.rollback()
            return failWithMessage("The mobile phone number or user name exists")
        except Exception as e:
            session.rollback()
            print(type(e))
            return failWithMessage(str(e))
        return ok()


@user.route('/login', methods=['POST'])
def login():
    if request.method == "POST":
        data = request.get_json()
        print(data)
        if not all([data.get('username'), data.get('password')]):
            return failWithMessage("User name and password are null")
        if len(data.get('username')) < 6 or len(data.get('password')) < 6:
            return failWithMessage("The username and password length is less than 6")
        user_model = session.query(User).filter_by(username=data['username'])
        if not user_model.first():
            return failWithMessage("user name does not exist ")
        if not user_model.first().check_password(data.get('password')):
            return failWithMessage("Password error")
        if all([data['latitude'], data['longitude']]):
            try:
                user_model.update({"latitude": data['latitude'], "longitude": data['longitude']})
                session.commit()
            except Exception as e:
                session.rollback()
                print(type(e))
                return failWithMessage(str(e))
        token = JWTUtils.generate_token(UserInfo.build_from_object(user_model.first()))
        redis_store.set(str(token), json.dumps(UserInfo.build_from_object(user_model.first())),
                        ex=baseConfig.REDIS_EXPIRES_TIME)
        return okWithData({"user": UserInfo.build_from_object(user_model.first()), "token": token})
