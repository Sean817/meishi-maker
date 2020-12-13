from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required, \
    current_user
from . import auth
from ..models import verify_password, User, Temp, generate_reset_password_confirmation_token, encrypt_passowrd, \
    generate_change_email_confirmation_token
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadSignature
from flask import current_app
from ..email import send_email
from .forms import LoginForm, RegistrationForm
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import time, json
from bson.objectid import ObjectId


@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.activate \
                and request.endpoint[:5] != 'auth.' \
                and request.endpoint != 'static':
            return redirect(url_for('auth.unconfirmed'))


@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.activate:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.objects(email=form.email.data).first()
        if user is not None and verify_password(user.password_hash, form.password.data):
            user = Temp(id=str(user.id), username=user.username, email=user.email,
                        password=user.password_hash, activate=user.activate, role=user.role, last_since=user.last_since,
                        member_since=user.member_since)
            login_user(user, form.remember_me.data)
            User.objects(email=form.email.data).update(last_since=datetime.utcnow())
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('Invalid username or password.')
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        User(email=form.email.data, username=form.username.data,
             password_hash=encrypt_passowrd(form.password.data)).save()
        user = User.objects.filter(email=form.email.data).first()
        temp = Temp(id=user.id, username=user.username, email=user.email,
                    password=user.password_hash, activate=False, role=user.role,
                    last_since=user.last_since, member_since=user.member_since)
        token = temp.generate_confirmation_token
        send_email(temp.email, 'Confirm Your Account',
                   'auth/temp/confirm', user=temp, token=token)
        flash('A confirmation temp has been sent to you by temp.')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    s = Serializer(current_app.config['SECRET_KEY'])
    try:
        s.loads(token)
    except BadSignature:
        return render_template('link_expired.html')
    data = s.loads(token)
    id = data.get('confirm')
    user = User.objects(id=ObjectId(id)).first()
    if user is None:
        flash('The confirmation link is invalid or has expired.')
    if user.activate:
        flash('this Account is already confirm')
        return redirect(url_for('main.index'))
    User.objects(id=ObjectId(id)).update(activate=True)
    time.sleep(0.5)
    flash('You have confirmed your account. Thanks!')
    return redirect(url_for('main.index'))


@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Confirm Your Account',
               'auth/email/confirm', user=current_user, token=token)
    flash('A new confirmation email has been sent to you by email.')
    return redirect(url_for('main.index'))
