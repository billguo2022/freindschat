import json

from flask import g, Blueprint, request
from sqlalchemy import exc, insert

from server.configs.config import baseConfig
from server.extensions import redis_store
from server.models import *
from server.models.response.group import GroupInfo
from server.models.response.res import *

group = Blueprint("group", __name__, url_prefix="/group")
"""
我的群聊操作：
获取我的群聊
修改我的群聊
添加群聊
解散群聊
"""


@group.route('/id', methods=['POST'])
def get_group_by_id():
    if request.method == "POST":
        data = request.get_json()
        print(data)
        try:
            my_groups = session.query(Group).filter_by(id=data.get('id')).first()
            group = GroupInfo.build_from_object(my_groups)
        except exc.IntegrityError:
            session.rollback()
            return fail()
        except Exception as e:
            session.rollback()
            print(type(e))
            return failWithMessage(str(e))
        finally:
            session.close()
        return okWithData(group)


@group.route('/get', methods=['GET'])
def get_my_group():
    try:
        jwt_user_id = g.user.id
        group_membership_obj = session.query(group_membership).filter_by(user_id=jwt_user_id)
        if group_membership_obj.first() is None:
            return failWithMessage("No group chat")
        my_group_ids = [i.group_id for i in group_membership_obj.all()]
        my_groups = session.query(Group).filter(Group.id.in_(my_group_ids), Group.owner_id == jwt_user_id).all()
        groups = [GroupInfo.build_from_object(i) for i in my_groups]

    except exc.IntegrityError:
        session.rollback()
        return fail()
    except Exception as e:
        session.rollback()
        print(type(e))
        return failWithMessage(str(e))
    finally:
        session.close()
    return okWithData({"groups": groups})


@group.route('/post', methods=['POST'])
def create_my_group():
    if request.method == "POST":
        data = request.get_json()
        print(data)
        if not all([data['name']]):
            return failWithMessage("Parameter error")
        if data.get('avatar'):
            avatar = data.get('avatar')[0]['url']
            group_obj = Group(name=data.get('name'), avatar=avatar)
        else:
            group_obj = Group(name=data.get('name'))
        try:
            jwt_user_id = g.user.id
            user = session.query(User).filter_by(id=jwt_user_id).first()
            group_obj.members.append(user)
            group_obj.owner_id = jwt_user_id
            session.add(group_obj)
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


@group.route('/put', methods=['PUT'])
def update_my_group():
    if request.method == "PUT":
        data = request.get_json()
        print(data)
        if not data['id']:
            return failWithMessage("Parameter error")
        if not data.get('name'):
            return failWithMessage("Parameter error")
        try:
            jwt_user_id = g.user.id
            group = session.query(Group).filter_by(id=data.get('id'))
            if group.first() is None:
                return failWithMessage("No group chat")
            if group.first().owner_id != jwt_user_id:
                return failWithMessage("illegality")
            group.update({Group.name: data.get('name'), Group.avatar: data.get('avatar')[0].get('url')})
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


@group.route('/delete', methods=['DELETE'])
def delete_my_group():
    if request.method == "DELETE":
        data = request.get_json()
        if not data['id']:
            return failWithMessage("Parameter error")
        try:
            jwt_user_id = g.user.id
            group = session.query(Group).filter_by(id=data.get('id'))
            if group.first() is None:
                return failWithMessage("No group chat")
            if group.first().owner_id != jwt_user_id:
                return failWithMessage("illegality")
            mygroup = session.query(group_membership).filter_by(user_id=jwt_user_id, group_id=group.first().id)
            if mygroup.first() is None:
                return failWithMessage("No group chat")
            mygroup.delete()
            session.query(ChatHistory).filter_by(group_id=data.get('id')).delete()
            session.query(Message).filter_by(group_id=data.get('id')).delete()
            group.delete()
            session.commit()
        except exc.IntegrityError:
            session.rollback()
            return fail()
        except Exception as e:
            session.rollback()
            print(e)
            print(type(e))
            return failWithMessage(str(e))
        finally:
            session.close()
        return ok()


"""
他人群聊操作：
我加入的群聊
查询群聊
退出一个群聊
加入一个群聊
"""


@group.route('/a/get', methods=['GET'])
def get_my_group_and_join():
    try:
        jwt_user_id = g.user.id
        group_membership_obj = session.query(group_membership).filter_by(user_id=jwt_user_id)
        if group_membership_obj.first() is None:
            return okWithData({"groups": []})
        my_group_ids = [i.group_id for i in group_membership_obj.all()]
        my_groups = session.query(Group).filter(Group.id.in_(my_group_ids)).all()
        groups = [GroupInfo.build_from_object(i) for i in my_groups]
    except exc.IntegrityError:
        session.rollback()
        return fail()
    except Exception as e:
        session.rollback()
        print(type(e))
        return failWithMessage(str(e))
    finally:
        session.close()
    return okWithData({"groups": groups})


@group.route('/a/select', methods=['POST'])
def select_a_group():
    if request.method == "POST":
        data = request.get_json()
        print(data)
        try:
            if data['kw']:
                group = session.query(Group).filter(
                    (Group.name == data.get('kw')) | (Group.number == data.get('kw'))).first()
            else:
                return failWithMessage("Parameter error")
            if group is None:
                return failWithMessage("No group chat")
            jwt_user_id = g.user.id
            if session.query(group_membership).filter_by(user_id=jwt_user_id, group_id=group.id).first():
                return failWithMessage("Already joined")
            group = GroupInfo.build_from_object(group)
        except exc.IntegrityError:
            session.rollback()
            return fail()
        except Exception as e:
            session.rollback()
            print(type(e))
            return failWithMessage(str(e))
        finally:
            session.close()
        return okWithData(group)


@group.route('/a/post', methods=['POST'])
def join_a_group():
    if request.method == "POST":
        data = request.get_json()
        print(data)
        if not data['id']:
            return failWithMessage("Parameter error")
        try:
            jwt_user_id = g.user.id
            group_obj = session.query(Group).filter_by(id=data.get('id')).first()
            user = session.query(User).filter_by(id=jwt_user_id).first()
            group_obj.members.append(user)
            session.add(group_obj)
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


@group.route('/a/delete', methods=['DELETE'])
def remove_a_group():
    if request.method == "DELETE":
        data = request.get_json()
        print(data)
        if data['id'] is None:
            return failWithMessage("Parameter error")
        try:
            jwt_user_id = g.user.id
            group = session.query(Group).filter_by(id=data.get('id')).first()
            if group is None:
                return failWithMessage("No group chat")
            jwt_user_id = g.user.id
            session.query(group_membership).filter_by(user_id=jwt_user_id, group_id=group.id).delete()
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
