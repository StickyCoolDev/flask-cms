import sqlalchemy as sa
from flask import render_template, redirect, url_for, request

from app import db, htmx
from app.models import SocialNetwork, Widget, Category, Tag
from app.widgets import bp

@bp.route('/about')
def about():
    if not htmx:
        return redirect('main.index')

    info = db.session.scalar(
        sa.select(Widget).where(Widget.name == 'about')
    )

    return render_template('partials/about.html', info=info)

@bp.route('/categories')
def categories():
    if not htmx:
        return redirect('main.index')

    categories = db.session.scalars(
        sa.select(Category).order_by(Category.category.asc())
    )

    return render_template('partials/categories.html', categories=categories)

@bp.route('/tags')
def tags():
    if not htmx:
        return redirect('main.index')
    
    tags = db.session.scalars(
        sa.select(Tag).order_by(Tag.tag.asc())
    )

    return render_template('partials/tags.html', tags=tags)
