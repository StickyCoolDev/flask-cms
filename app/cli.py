import os
from flask import Blueprint
import click
from click import ClickException
from markdown import Markdown
import re
from slugify import slugify
import sqlalchemy as sa
from datetime import datetime, timezone

from app import db
from app.models import Post, User, Category, Tag

bp = Blueprint('cli', __name__, cli_group=None)
md = Markdown(extensions=['meta'])

## Utilities

def _process_file(path : str):
    if not os.path.isfile(path):
        raise ClickException('File not found')
    
    regexp = r'\.(md|txt)$'

    if re.search(regexp, path, re.IGNORECASE) is None:
        raise ClickException('Invalid file extension. Valid extensions: .md, .txt')
    
    filename = os.path.split(path)[1]
    slug = slugify(os.path.splitext(filename)[0])
    
    with open(path, 'r') as file:
        md_content = file.read()

    html = md.convert(md_content)

    if not 'title' in md.Meta.keys():
        raise ClickException('Title not found')
    
    if not 'author' in md.Meta.keys():
        raise ClickException('Author not found')
    
    if not 'category' in md.Meta.keys():
        raise ClickException('Category not found')

    category = Category.find_category(md.Meta['category'][0], create_if_not_exists=True)

    author = db.session.scalar(
        sa.select(User).where(User.username == md.Meta['author'][0])
    )

    if author is None:
        raise ClickException('Author doesn\'t exist in database')
    
    taglist = []
    if 'tags' in md.Meta.keys():
        for tag in md.Meta['tags']:
            taglist.append(Tag.find_tag(tag, create_if_not_exists=True))

    post = Post.get_by_slug(slug)
    if post is None:
        post = Post(slug=slug, author=author, category=category, title=md.Meta['title'][0], body=html)
        db.session.add(post)
    else:
        post.last_modified = datetime.now(timezone.utc)
        post.author = author
        post.body = html
        post.category = category
        post.title = md.Meta['title'][0]
    
    if len(taglist) > 0:
        post.add_tags(taglist)

    db.session.commit()


## Cli groups

@bp.cli.group()
def file():
    """Upload and process files"""
    pass

@bp.cli.group()
def user():
    """User management"""
    pass

## File commands

@file.command()
@click.argument('files', nargs=-1)
def upload(files : tuple[str, ...]):
    """Upload a list of files to CMS"""
    with click.progressbar(files, label='Processing files') as bar:
        for file in bar:
            try:
                _process_file(file)
            except ClickException as e:
                e.show()
                db.session.rollback()
    
    click.echo('Upload complete!')

## User commands

@user.command()
@click.argument('username')
@click.argument('email')
@click.option('--fullname', prompt='Full name', help='User full name')
@click.option('-a', '--admin', is_flag=True, help='User has admin privileges')
@click.option('-e', '--edit', is_flag=True, help='User is editor')
@click.option('-m', '--mod', is_flag=True, help='User is moderator')
def create(username, email, fullname, admin, edit, mod):
    """Create a new user"""
    user = User(username=username, email=email, fullname=fullname)
    db.session.add(user)

    #TODO Roles

    db.session.commit()

@user.command()
@click.argument('username')
def delete(username):
    """Delete user"""
    pass