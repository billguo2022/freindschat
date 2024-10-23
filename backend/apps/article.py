from flask import g, Blueprint, request
from sqlalchemy import exc

from server.models import *
from server.models.response.res import *
from server.models.response.article import *

article = Blueprint("article", __name__, url_prefix="/article")


# 查询我的朋友圈
@article.route('/get', methods=['GET'])
def get_my_pyq():
    try:
        jwt_user_id = g.user.id
        friends = session.query(Friend).filter_by(user_id=jwt_user_id).all()
        sender_ids = [i.friend_id for i in friends]
        sender_ids.append(jwt_user_id)
        articles = session.query(Article).filter(
            Article.sender_id.in_(sender_ids)).order_by(
            -Article.created_at).all()
        articleInfos = [ArticleInfo.build_from_object(i, session.query(ArticleLike).filter_by(article_id=i.id).all(),
                                                      session.query(Comment).filter_by(article_id=i.id).all())
                        for i in
                        articles]
        print(articleInfos)
    except exc.IntegrityError:
        session.rollback()
        return fail()
    except Exception as e:
        session.rollback()
        print(type(e))
        return failWithMessage(str(e))
    finally:
        session.close()
    return okWithData({"articles": articleInfos})


# 发表动态
@article.route('/post', methods=['POST'])
def create_my_pyq():
    if request.method == "POST":
        data = request.get_json()
        print(data)
        urls = ''
        jwt_user_id = g.user.id
        if not data['content']:
            return failWithMessage("parameter error ")
        if data.get('image'):
            for index, i in enumerate(data.get('image')):
                url = i['url']
                if index == len(data.get('image')) - 1:
                    urls = urls + url
                else:
                    urls = urls + url + ';'
        if data.get('video'):
            video = data.get('video')[0]['url']
        else:
            video = ''
        article = Article(sender_id=jwt_user_id, content=data.get('content'), image_url=urls,
                          video_url=video)
        try:
            session.add(article)
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


# 修改动态
@article.route('/update', methods=['PUT'])
def update_my_pyq():
    if request.method == "PUT":
        data = request.get_json()
        print(data)
        urls = ''
        if not data['id']:
            return failWithMessage("parameter error ")
        if not data['content']:
            return failWithMessage("parameter error ")
        if data.get('image'):
            for index, i in enumerate(data.get('image')):
                url = i['url']
                if index == len(data.get('image')) - 1:
                    urls = urls + url
                else:
                    urls = urls + url + ';'
        if data.get('video'):
            video = data.get('video')[0]['url']
        else:
            video = ''
        article = {Article.content: data.get('content'), Article.image_url: urls, Article.video_url: video}
        try:
            article_obj = session.query(Article).filter_by(id=data.get('id'))
            if article_obj.first() is None:
                return failWithMessage("There is no such update")
            article_obj.update(article)
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


# 删除动态
@article.route('/delete', methods=['DELETE'])
def delete_my_pyq():
    if request.method == "DELETE":
        data = request.get_json()
        print(data)
        if not data['id']:
            return failWithMessage("parameter error ")
        try:
            article = session.query(Article).filter_by(id=data.get('id'))
            if article.first() is None:
                return failWithMessage("There is no such update")
            article.delete()
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


# 点赞
@article.route('/like', methods=['POST'])
def like():
    if request.method == "POST":
        data = request.get_json()
        print(data)
        jwt_user_id = g.user.id
        if not data['id']:
            return failWithMessage("parameter error ")
        try:
            article = session.query(Article).filter_by(id=data.get('id'))
            if article.first() is None:
                return failWithMessage("There is no such update")
            session.add(ArticleLike(article_id=data['id'], user_id=jwt_user_id))
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


# 取消点赞
@article.route('/unlike', methods=['POST'])
def unlike():
    if request.method == "POST":
        data = request.get_json()
        print(data)
        jwt_user_id = g.user.id
        if not data['id']:
            return failWithMessage("parameter error ")
        try:
            article = session.query(Article).filter_by(id=data.get('id'))
            if article.first() is None:
                return failWithMessage("There is no such update")
            al = session.query(ArticleLike).filter_by(article_id=data['id'], user_id=jwt_user_id)
            if al.first() is None:
                return failWithMessage("No likes available")
            al.delete()
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


# 评论
@article.route('/comment', methods=['POST'])
def comment():
    if request.method == "POST":
        data = request.get_json()
        print(data)
        jwt_user_id = g.user.id
        if not data['article_id']:
            return failWithMessage("参数错误")
        if not data['content']:
            return failWithMessage("参数错误")
        try:
            article = session.query(Article).filter_by(id=data.get('article_id'))
            if article.first() is None:
                return failWithMessage("There is no such update")
            session.add(Comment(article_id=data['article_id'], user_id=jwt_user_id, content=data.get('content')))
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


# 评论
@article.route('/comment', methods=['DELETE'])
def comment_del():
    if request.method == "DELETE":
        data = request.get_json()
        print(data)
        if not data['id']:
            return failWithMessage("parameter error ")
        try:
            session.query(Comment).filter_by(id=data.get('id')).delete()
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
