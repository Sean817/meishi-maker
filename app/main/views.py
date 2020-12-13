from flask import render_template, abort, flash, request, current_app, make_response, redirect, url_for
from . import main
from ..models import User, Temp, Permission, Post, body_html
from flask_login import login_required, current_user
from .forms import EditProfileForm, EditProfileAdminForm, PostForm, EditPostForm, CommentForm
from ..decorators import admin_required, permission_required

# from ..decorators import admin_required, permission_required
from bson.objectid import ObjectId
from datetime import datetime


# @main.route('/', methods=['GET', 'POST'])
# def index():
#     form = PostForm()
#     if current_user.can(Permission.WRITE_ARTICLES) and \
#             form.validate_on_submit():
#         Post(body=form.body.data).new_article()
#         return redirect(url_for('.index'))
#     # page = request.args.get('page', 1, type=int)
#     show_followed = True
#     if current_user.is_authenticated:
#         show_followed = bool(request.cookies.get('show_followed', ''))
#     return render_template('index.html', form=form, show_followed=show_followed)

@main.route('/', methods=['GET', 'POST'])
def index():
    form = PostForm()
    if current_user.can(Permission.WRITE_ARTICLES) and \
            form.validate_on_submit():
        Post(body=form.body.data).new_article()
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    show_followed = True
    if current_user.is_authenticated:
        show_followed = bool(request.cookies.get('show_followed', ''))
    # if show_followed:
    #     pagination = Paginate(page, 1)
    # else:
    #     pagination = Paginate(page, 0)
    posts = []
    return render_template('index.html', form=form, posts=posts,  show_followed=show_followed)

# @main.route('/post/<id>', methods=['GET', 'POST'])
# def post(id):
#     post = MongoClient().blog.Aritical.find({'_id': ObjectId(id)})
#     form = CommentForm()
#     if form.validate_on_submit():
#         comments = post[0].get('comments')
#         body = form.body.data
#         comments.append([body, current_user.username, datetime.utcnow()])
#         MongoClient().blog.Aritical.update({'_id': ObjectId(id)}, {'$set': {'comments': comments}})
#         flash('评论发布成功.')
#         return redirect(url_for('.post', id=id, page=-1))
#     page = request.args.get('page', 1, type=int)
#     pagination = PaginateComments(page, id)
#     comments = pagination.items
#     comment = (post[0].get('username') != current_user.username)
#     return render_template('post.html', posts=post, form=form, i=0,
#                            comments=comments, pagination=pagination, author=comment, id=id)

@main.route('/all')
@login_required
def show_all():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '', max_age=30 * 24 * 60 * 60)
    return resp


@main.route('/followed')
@login_required
def show_followed():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '1', max_age=30 * 24 * 60 * 60)
    return resp


@main.route('/user/<username>')
@login_required
def user(username):
    user_temp = User.objects(username=username).first()
    if user_temp is None:
        abort(404)
    user = Temp(id=user_temp.id, username=user_temp.username, email=user_temp.email,
                password=user_temp.password_hash, activate=user_temp.activate, role=user_temp.role,
                last_since=user_temp.last_since, member_since=user_temp.member_since)
    # page = request.args.get('page', 1, type=int)
    # pagination = PaginateUser(page, username)
    # posts = pagination.item
    followers = user_temp.followers
    following = user_temp.following
    return render_template('user.html', user=user, followers=followers,
                           following=following)


@main.route('/following/<username>')
def following(username):
    follows = User.objects(username=username).first().following
    if user is None:
        flash('此用户不存在.')
        return redirect(url_for('.index'))
    # page = request.args.get('page', 1, type=int)
    return render_template('followers.html', user=user, title='关注的人', title1='', title2='关注的人',
                           endpoint='.following', follows=follows)


@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user = User.objects(username=username).first()
    if user is None:
        flash('此用户不存在.')
        return redirect(url_for('.index'))
    very = False
    temp = User.objects(username=current_user.username).first().following
    for i in range(temp.__len__()):
        if temp[i][0] == username:
            very = True
            break
    if very:
        flash('您已经关注过了他，不能重复关注.')
        return redirect(url_for('.user', username=username))
    followers = user.followers
    time = datetime.utcnow()
    follow = [current_user.username, time]
    followers.append(follow)
    User.objects(username=username).update(followers=followers)
    post2 = User.objects(username=current_user.username).first()
    following = post2.following
    follow = {'username': user.username, 'timestamp': time}
    following.append(follow)
    User.objects(username=current_user.username).update(following=following)
    flash('您成功关注了 %s.' % username)
    return redirect(url_for('.user', username=username))


@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    user = User.objects(username=username).first()
    if user is None:
        flash('此用户不存在.')
        return redirect(url_for('.index'))
    very = False
    temp = User.objects(username=current_user.username).following
    for i in range(temp.__len__()):
        if temp[i][0] == username:
            very = True
            break
    if not very:
        flash('您没有关注这个用户.')
        return redirect(url_for('.user', username=username))
    followers = user.followers
    for i in range(followers.__len__()):
        if followers[i][0] == current_user.username:
            followers.remove(followers[i])
            break
    User.objects(username=username).update(followers=followers)
    post2 = User.objects(username=current_user.username).first()
    following = post2.following
    for i in range(following.__len__()):
        if following[i][0] == username:
            following.remove(following[i])
            break
    User.objects(username=current_user.username).update(following=following)
    flash('您取消关注了 %s.' % username)
    return redirect(url_for('.user', username=username))


@main.route('/followers/<username>')
def followers(username):
    follows = User.objects(username=username).first().followers
    if user is None:
        flash('此用户不存在.')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    # pagination = PaginateFollowers(page=page, username=username)
    # follows = pagination.item
    return render_template('followers.html', user=user, title="关注", title1='关注', title2='的人',
                           endpoint='.followers', follows=follows)
