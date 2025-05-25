import sqlalchemy as sa
from flask import current_app, redirect, render_template, url_for, request, flash
from flask_login import current_user, login_user
from urllib.parse import urlsplit

from app import db, htmx
from app.models import User
from app.auth import bp
from app.auth.forms import LoginForm, RegisterForm

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated and not htmx:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data)
        )

        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))
        
        login_user(user, remember=form.remember.data)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('main.index')

        return redirect(next_page)

    if htmx:
        return render_template('auth/partials/login.html', form=form)
    
    return render_template('auth/login.html', title='Sign In', form=form)
            

@bp.route('/register', methods=['GET','POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            username = form.username.data,
            fullname = form.fullname.data,
            email = form.email.data
        )
        user.set_password(form.password.data)
        db.session.add(user)

        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', title='Register', form=form)

@bp.route('/validate_email/<token>', methods=['GET','POST'])
def validate_email(token: str):
    pass

@bp.route('/reset_password_request', methods=['GET','POST'])
def reset_password_request():
    pass

@bp.route('reset_password/<token>', methods=['GET','POST'])
def reset_password(token: str):
    pass

