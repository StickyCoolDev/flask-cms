import sqlalchemy as sa
from flask import render_template, url_for, request, current_app, g

from app import db, htmx
from app.models import Category, Tag, User, Post, Widget
from app.main import bp

@bp.before_app_request
def before_request():
    query = sa.select(Widget).where(Widget.is_active == True)
    widget_count = db.session.scalar(
        sa.select(sa.func.count()).select_from(query)
    )
    g.cms_widgets = db.session.scalars(query.order_by(Widget.order.asc()))
    g.cms_has_active_widgets = widget_count > 0

@bp.route('/')
@bp.route('/index')
def index():
    page = request.args.get('page', 1, type=int)
    query = sa.select(Post).order_by(Post.timestamp.desc())
    posts = db.paginate(query, page=page,
                        per_page=current_app.config['PER_PAGE'],
                        error_out=False)
    next_url = url_for('main.index', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.index', page=posts.prev_num) \
        if posts.has_prev else None
    
    if htmx:
        return render_template('partials/index.html', posts=posts.items,
                               next_url=next_url, prev_url=prev_url)
    
    return render_template('index.html', title='Home', posts=posts.items,
                           next_url=next_url, prev_url=prev_url)

@bp.route('/about')
def about():
    info = db.session.scalar(
        sa.select(Widget).where(Widget.name == 'about')
    )

    return render_template('about.html', title='About me', info=info)

@bp.route('/post/<slug>', methods=['GET','POST'])
def post(slug : str):
    post : Post= db.first_or_404(
        sa.select(Post).where(Post.slug == slug)
    )

    return render_template('post.html', post=post, title=post.title)


@bp.route('/tag/<tagname>')
def tag(tagname : str):
    tag : Tag = db.first_or_404(
        sa.select(Tag).where(Tag.tag == tagname)
    )

    query = sa.select(Post).select_from(tag.posts.select()).order_by(Post.timestamp.desc())
    page = request.args.get('page', 1, type=int)
    posts = db.paginate(query, per_page=current_app.config['PER_PAGE'],
                        page=page, error_out=False)
    prev_url = url_for('main.tag', tagname=tagname, page=posts.prev_num) \
        if posts.has_prev else None
    next_url = url_for('main.tag', tagname=tagname, page=posts.next_num) \
        if posts.has_next else None
    
    if htmx:
        return render_template('partials/index.html', posts=posts.items,
                               next_url=next_url, prev_url=prev_url)
    
    title = 'Tag: {}'.format(tagname)
    return render_template('index.html', posts=posts.items, title=title,
                           next_url=next_url, prev_url=prev_url)

@bp.route('/category/<categoryname>')
def category(categoryname : str):
    category : Category = db.first_or_404(
        sa.select(Category).where(Category.category == categoryname)
    )
    query = sa.select(Post).select_from(category.posts.select()).order_by(Post.timestamp.desc())
    page = request.args.get('page', 1, type=int)
    posts = db.paginate(query, page=page,
                        per_page=current_app.config['PER_PAGE'],
                        error_out=False)
    prev_url = url_for('main.category', categoryname=categoryname, page=posts.prev_num) \
        if posts.has_prev else None
    next_url = url_for('main.category', categoryname=categoryname, page=posts.next_num) \
        if posts.has_next else None
    
    if htmx:
        return render_template('partials/index.html', posts=posts,
                               prev_url=prev_url, next_url=next_url)
    
    title = 'Category: {}'.format(categoryname)
    return render_template('index.html', title=title, posts=posts,
                           prev_url=prev_url, next_url=next_url)

@bp.route('/user/<username>')
def user(username : str):
    user : User = db.first_or_404(
        sa.select(User).where(User.username == username)
    )

    page = request.args.get('page', 1, type=int)
    posts = db.paginate(user.posts.select(), page=page,
                        per_page=current_app.config['PER_PAGE'],
                        error_out=False)
    
    prev_url = url_for('main.user', username=username, page=posts.prev_num) \
        if posts.has_prev else None
    next_url = url_for('main.user', username=username, page=posts.next_num) \
        if posts.has_next else None
    
    if htmx:
        return render_template('partials/index.html', posts=posts.items, 
                               next_url=next_url, prev_url=prev_url)
    
    title = 'User: {}'.format(user.fullname)
    return render_template('user.html', user=user, posts=posts.items,
                           prev_url=prev_url, next_url=next_url, title=title)