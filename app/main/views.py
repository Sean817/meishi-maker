from flask import render_template, abort, flash, request, current_app, make_response, redirect, url_for
from . import main
from ..models import User, Temp, Permission, Moment
from flask_login import login_required, current_user
from .forms import EditProfileForm, EditProfileAdminForm, EditPostForm, CommentForm, MomentForm
from ..decorators import admin_required, permission_required
from flask_uploads import UploadSet, IMAGES
from ..create_path import create_path
from werkzeug.utils import secure_filename
# from ..decorators import admin_required, permission_required
from datetime import datetime
from config import basedir
import time
import hashlib


class Paginate:
    def __init__(self, page, show_follow):
        if show_follow == 0:
            posts = Moment.objects.order_by('-issuing_time')
            self.total = posts.count()
            self.posts = posts
        if show_follow == 1:
            self.posts = []
            following = User.objects(username=current_user.username).first().following
            moment = Moment.objects.order_by('-issuing_time')
            # following.append([current_user.username, 'date'])
            for i in range(following.__len__()):
                for x in range(moment.count()):
                    if following[i][0] == moment[x].get('username'):
                        self.posts.append(moment[x])
                        self.posts.sort(key=lambda x: x.get('issuing_time'), reverse=True)
            self.total = self.posts.__len__()
        self.pages = int(self.total / 20)
        if self.total % 20 != 0:
            self.pages += 1
        if page == 1:
            self.has_prev = False
        else:
            self.has_prev = True
        if page == self.pages:
            self.has_next = False
        else:
            self.has_next = True
        self.next_num = page + 1
        self.page = page
        self.per_page = 20
        self.prev_num = page - 1
        self.current_num = self.total - (20 * (page - 1))
        if self.current_num > 20:
            self.current_num = 20
        self.item = []
        for i in range(self.current_num):
            self.item.append(self.posts[self.prev_num * 20 + i])

    def iter_pages(self, left_edge=2, left_current=2,
                   right_current=5, right_edge=2):
        last = 0
        for num in range(1, self.pages + 1):
            if num <= left_edge or \
                    (self.page - left_current - 1 < num < self.page + right_current) \
                    or num > self.pages - right_edge:
                if last + 1 != num:
                    yield None
                yield num
                last = num

@main.route('/', methods=['GET', 'POST'])
def index():
    page = request.args.get('page', 1, type=int)
    show_followed = False
    if current_user.is_authenticated:
        show_followed = bool(request.cookies.get('show_followed', ''))
    if show_followed:
        pagination = Paginate(page, 1)
    else:
        pagination = Paginate(page, 0)
    posts = pagination.item
    return render_template('index.html', posts=posts, pagination=pagination, show_followed=show_followed)


@main.route('/moment', methods=['GET', 'POST'])
@login_required
def moment():
    form = MomentForm()
    file_url_list = []
    if form.validate_on_submit():
        dir_path = basedir + '/app/static/moment_pic/'
        upload_path = create_path(dir_path)
        photos = UploadSet('photos', IMAGES)
        for filename in request.files.getlist('photo'):
            name = hashlib.md5((current_user.username + str(time.time())).encode('utf8')).hexdigest()[:15]
            filename = photos.save(filename, folder=upload_path, name=name + '.')
            # print(filename)
            file_url = photos.url(filename)
            file_url_list.append(file_url)
            # print(file_url)
        Moment(username=current_user.username, picture=file_url_list,
               content=form.content.data, user_id=current_user.id).save()
        flash('发布成功！', 'success')
        return redirect(url_for('.index'))
    else:
        pass
    return render_template('post_moment.html', form=form, file_url_list=file_url_list)


@main.route('/all')
@login_required
def show_all():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '', max_age=30 * 24 * 60 * 60)
    return resp


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
