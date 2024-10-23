import random
from datetime import datetime, timedelta

from flask import g, Blueprint, request
from haversine import haversine
from sqlalchemy import exc

from server.extensions import redis_store
from server.models import session, User, Friend, TemporarilyBottle
from server.models.response.friend import FriendInfo, TemporarilyBottleInfo
from server.models.response.res import fail, failWithMessage, ok, okWithData, failLocation
from server.models.response.user import UserInfo

bottle = Blueprint("bottle", __name__, url_prefix="/bottle")


def check_request_limit_h(user_id):
    now = datetime.now()
    key = f'request_limit:{user_id}'

    # 获取上次请求的时间
    last_request_time = redis_store.get(key)

    if last_request_time is None:
        # 如果是第一次请求或者已经过了六个小时，则设置请求时间为当前时间
        last_request_time = now.strftime('%Y-%m-%d %H:%M:%S')
        expiration = 6 * 60 * 60  # 设置过期时间为六个小时
        redis_store.set(key, last_request_time, ex=expiration)
    else:
        # 将存储的时间字符串转换为datetime类型进行比较
        last_request_time = datetime.strptime(last_request_time, '%Y-%m-%d %H:%M:%S')

        # 计算与上次请求的时间差
        time_diff = now - last_request_time

        if time_diff.total_seconds() < 6 * 60 * 60:
            # 如果距离上次请求的时间未超过六个小时，则不允许再次请求
            return False
        else:
            # 更新上次请求的时间为当前时间，并设置过期时间
            last_request_time = now.strftime('%Y-%m-%d %H:%M:%S')
            expiration = 6 * 60 * 60  # 设置过期时间为六个小时
            redis_store.set(key, last_request_time, ex=expiration)
    return True


# 定义函数来判断用户请求次数是否超过限制
def check_request_limit_d(user_id, limit=3):
    today = datetime.now().strftime('%Y-%m-%d')
    key = f'request_limit:{user_id}:{today}'

    # 获取当前用户今天已经请求的次数
    count = redis_store.get(key)

    if count is None:
        # 如果是第一次请求，则设置初始计数器，并设置过期时间为到明天零点的时间差
        count = 0
        expiration = (datetime.combine(datetime.now().date() + timedelta(days=1),
                                       datetime.min.time()) - datetime.now()).seconds
        redis_store.set(key, count, ex=expiration)

    count = int(count)

    # 增加请求次数
    count += 1
    redis_store.set(key, count)

    # 判断请求次数是否超过限制
    if count > limit:
        return False
    else:
        return True


# 捡一个
@bottle.route('/pick', methods=['GET', "POST"])
def pick():
    jwt_user_id = g.user.id
    '''
    去获取距离当前用户最近的用户
    '''
    if request.method == "GET":
        target_user = session.query(User).filter_by(id=jwt_user_id).first()
        if not all([target_user.latitude, target_user.longitude]):
            return failLocation()
        if not check_request_limit_h(jwt_user_id):
            return failWithMessage("Please wait")
        target_location = (float(target_user.latitude), float(target_user.longitude))

        tb = [i.friend_id for i in session.query(TemporarilyBottle).filter_by(user_id=jwt_user_id).all()]

        # 我的朋友
        my_friends = session.query(User).filter(User.id.in_(
            [i.friend_id for i in session.query(Friend).filter_by(user_id=jwt_user_id, status=1).all()])).all()
        my_friends_ids = [i.id for i in my_friends]
        all_users = session.query(User).all()

        # 计算距离并找到最近的三个用户
        closest_users = []
        min_distances = []

        for user in all_users:
            if user.id == jwt_user_id:
                continue  # 跳过目标用户自身
            if user.id in my_friends_ids:
                continue  # 跳过朋友
            if user.id in tb:
                continue  # 跳过已经存在的盒子
            if not all([user.latitude, user.longitude]):
                continue
            user_location = (float(user.latitude), float(user.longitude))
            distance = haversine(target_location, user_location)
            if len(closest_users) < 3:
                closest_users.append({"user": user, "distance": distance})
                min_distances.append(distance)
            else:
                max_distance = max(min_distances)
                if distance < max_distance:
                    max_index = min_distances.index(max_distance)
                    closest_users[max_index] = {"user": user, "distance": distance}
                    min_distances[max_index] = distance
        if len(closest_users) == 0:
            print("未找到最近的用户")
            return failWithMessage("No recent user found")
        else:
            random_dict = random.choice(closest_users)
            print("最近的用户是：", random_dict['user'].username)
            print("距离：", random_dict['distance'], "km")
            random_user = random_dict['user']
            u = UserInfo.build_from_object(random_user)
            random_distance = random_dict['distance']
            try:
                tb = TemporarilyBottle(user_id=jwt_user_id, friend_id=random_user.id, distance=random_distance)
                session.add(tb)
                session.commit()
            except Exception as e:
                session.rollback()
                print(type(e))
                return failWithMessage(str(e))
            finally:
                session.close()
            return okWithData({"user": u,
                               "distance": random_distance})
    if request.method == "POST":
        try:
            data = request.get_json()
            print(data)
            session.add(Friend(user_id=jwt_user_id, friend_id=data['id'], type_number=1, state=True))
            session.add(Friend(user_id=data['id'], friend_id=jwt_user_id, type_number=1))
            session.query(TemporarilyBottle).filter_by(user_id=jwt_user_id, friend_id=data['id']).update(
                {"state": True})
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


# 我的瓶子
@bottle.route('/my', methods=['GET', "DELETE"])
def my():
    if request.method == "GET":
        jwt_user_id = g.user.id
        bottles = session.query(Friend).filter_by(user_id=jwt_user_id, status=1, type_number=1).all()
        return okWithData({"bottles": [FriendInfo.build_from_object(i) for i in bottles]})
    if request.method == "DELETE":
        try:
            data = request.get_json()
            print(data)
            if not data['id']:
                return failWithMessage("Parameter error")
            session.query(Friend).filter_by(id=data.get('id')).delete()
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


# 获取临时的盒子
@bottle.route('/get_temporarily_bottle', methods=['GET'])
def get_temporarily_bottle():
    if request.method == "GET":
        jwt_user_id = g.user.id
        bottles = session.query(TemporarilyBottle).filter(
            (TemporarilyBottle.user_id == jwt_user_id) | (TemporarilyBottle.friend_id == jwt_user_id)).all()

        return okWithData({"bottles": [TemporarilyBottleInfo.build_from_object(i, session.query(Friend).filter_by(
            user_id=i.user_id, friend_id=i.friend_id).first().id if session.query(Friend).filter_by(
            user_id=i.user_id, friend_id=i.friend_id).first() else None) for i in bottles]})
