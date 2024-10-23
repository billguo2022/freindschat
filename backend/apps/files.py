import os
import uuid

from flask import Blueprint, request, g
from sqlalchemy import exc

from server.configs.config import baseConfig
from server.models import session, User, Group
from server.models.response.res import fail, failWithMessage, okWithData

file = Blueprint("file", __name__, url_prefix="/file")


@file.route('/avatar', methods=['POST'])
def upload_avatar_user():
    if 'file' not in request.files:
        return failWithMessage("parameter error ")
    avatar = request.files['file']
    extension = os.path.splitext(avatar.filename)[1]  # 获取文件扩展名
    avatar.filename = str(uuid.uuid4()) + extension  # 生成新的文件名
    avatar.save(os.path.join(baseConfig.UPLOADED_PHOTOS_DEST, avatar.filename))
    try:
        url = request.host_url + baseConfig.UPLOADED_PHOTOS_URL + avatar.filename
        print(request.host_url)
        print(request.origin)
        session.query(User).filter_by(id=g.get('user').id).update(
            {"avatar": url})
        session.commit()
    except exc.IntegrityError:
        session.rollback()
        return fail()
    except Exception as e:
        session.rollback()
        print(type(e))
        return failWithMessage(str(e))
    return okWithData(url)


@file.route('/avatar/group', methods=['POST'])
def upload_avatar_group():
    if 'file' not in request.files:
        return failWithMessage("parameter error ")
    avatar = request.files['file']
    extension = os.path.splitext(avatar.filename)[1]  # 获取文件扩展名
    avatar.filename = str(uuid.uuid4()) + extension  # 生成新的文件名
    avatar.save(os.path.join(baseConfig.UPLOADED_PHOTOS_DEST, avatar.filename))
    url = request.host_url + baseConfig.UPLOADED_PHOTOS_URL + avatar.filename
    return okWithData(url)


@file.route('/audio', methods=['POST'])
def upload_audio():
    audio_file = request.files['audio']
    extension = os.path.splitext(audio_file.filename)[1]  # 获取文件扩展名
    audio_file.filename = str(uuid.uuid4()) + extension  # 生成新的文件名
    audio_file.save(os.path.join(baseConfig.UPLOADED_PHOTOS_DEST, audio_file.filename))
    url = request.host_url + baseConfig.UPLOADED_PHOTOS_URL + audio_file.filename
    return okWithData(url)


# 允许上传的文件类型
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


# 检查文件扩展名是否合法
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@file.route('/upload', methods=['POST'])
def upload_files():
    # 检查是否有文件被上传
    if 'files' not in request.files:
        return failWithMessage("parameter error ")
    avatars = request.files.getlist('files')
    urls = []
    for avatar in avatars:
        # 检查文件扩展名是否合法
        if avatar and allowed_file(avatar.filename):
            extension = os.path.splitext(avatar.filename)[1]  # 获取文件扩展名
            avatar.filename = str(uuid.uuid4()) + extension  # 生成新的文件名
            avatar.save(os.path.join(baseConfig.UPLOADED_PHOTOS_DEST, avatar.filename))
            url = request.host_url + baseConfig.UPLOADED_PHOTOS_URL + avatar.filename
            print(request.host_url)
            print(request.origin)
            urls.append(url)
    return okWithData(urls)
