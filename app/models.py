from app import db, login
import sqlalchemy as sa
from sqlalchemy import event
import sqlalchemy.orm as so
from typing import Optional, Union
from datetime import datetime, timedelta, timezone
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash



post_tags = sa.Table('post_tags', db.metadata,
                     sa.Column('post_id', sa.Integer, sa.ForeignKey('post.id')),
                     sa.Column('tag_id', sa.Integer, sa.ForeignKey('tag.id')),
                     )

class User(db.Model, UserMixin):
    id : so.Mapped[int] = so.mapped_column(primary_key=True)
    username : so.Mapped[str] = so.mapped_column(sa.String(64), unique=True, index=True)
    fullname : so.Mapped[str] = so.mapped_column(sa.String(128))
    email : so.Mapped[str] = so.mapped_column(sa.String(256), unique=True, index=True)
    password_hash : so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    about_me : so.Mapped[Optional[str]] = so.mapped_column(sa.Text)
    joined : so.Mapped[datetime] = so.mapped_column(sa.DateTime, default=lambda: datetime.now(timezone.utc))
    last_seen : so.Mapped[datetime] = so.mapped_column(sa.DateTime, default=lambda: datetime.now(timezone.utc))
    posts : so.WriteOnlyMapped['Post'] = so.relationship(back_populates='author')


    def __repr__(self):
        return '<User {}>'.format(self.username)
    
    def set_password(self, password : str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password : str):
        return check_password_hash(self.password_hash, password)
    
    @staticmethod
    def anonymous_user(email : str, username : str, create_if_not_exists=False):
        user = db.session.scalar(
            sa.select(User).where(User.email == email)
        )

        if user is None and create_if_not_exists:
            user = User(username=username, fullname=username, email=email)
            db.session.add(user)
            db.session.commit()

        return user
        
    
@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))

class Post(db.Model):
    id : so.Mapped[int] = so.mapped_column(primary_key=True)
    slug : so.Mapped[str] = so.mapped_column(sa.String(128), index=True, unique=True)
    title : so.Mapped[str] = so.mapped_column(sa.String(512))
    body : so.Mapped[str] = so.mapped_column(sa.Text, deferred=True)
    resume : so.Mapped[Optional[str]] = so.mapped_column(sa.Text, deferred=True)
    timestamp : so.Mapped[datetime] = so.mapped_column(sa.DateTime, default=lambda: datetime.now(timezone.utc))
    last_modified : so.Mapped[datetime] = so.mapped_column(sa.DateTime, default=lambda: datetime.now(timezone.utc))
    user_id : so.Mapped[int] = so.mapped_column(sa.ForeignKey('user.id'), index=True)
    author : so.Mapped['User'] = so.relationship(back_populates='posts')
    category_id : so.Mapped[int] = so.mapped_column(sa.ForeignKey('category.id'), index=True)
    category : so.Mapped['Category'] = so.relationship(back_populates='posts')
    tags : so.WriteOnlyMapped['Tag'] = so.relationship(secondary=post_tags, back_populates='posts')

    def __repr__(self):
        return '<Post {}>'.format(self.title)
    
    def has_tags(self) -> bool:
        tag_count = db.session.scalar(
            sa.select(sa.func.count()).select_from(self.tags.select())
        )

        return tag_count > 0
    
    @property
    def taglist(self):
        return db.session.scalars(self.tags.select())
    
    
    def comment_count(self):
        return db.session.scalar(
            sa.select(sa.func.count()).select_from(self.comments.select())
        )
    
    def _in_taglist(self, tag_id: int):
        query = self.tags.select().where(Tag.id == tag_id)
        return db.session.scalar(query) is not None
    
    def add_tags(self, tags: Union['Tag', list]):
        if isinstance(tags, Tag):
            tags = [ tags ]

        for tag in tags:
            if not self._in_taglist(tag.id):
                self.tags.add(tag)

    def remove_tags(self, tags: Union['Tag', list]):
        if isinstance(tags, Tag):
            tags = [ tags ]

        for tag in tags:
            if self._in_taglist(tag.id):
                self.tags.remove(tag)

    @staticmethod
    def get_by_slug(slug: str):
        return db.session.scalar(
            sa.select(Post).where(Post.slug == slug)
        )

@event.listens_for(Post, 'before_insert')
def get_resume(mapper, connect, target):
    target.resume = target.body[:(target.body.find('</p>') + 4)]

class Category(db.Model):
    id : so.Mapped[int] = so.mapped_column(primary_key=True)
    category : so.Mapped[str] = so.mapped_column(sa.String(128))
    posts : so.WriteOnlyMapped['Post'] = so.relationship(back_populates='category')

    def __repr__(self):
        return '<Category {}>'.format(self.category)
    
    @staticmethod
    def find_category(cat : str, create_if_not_exists=False):
        category = db.session.scalar(
            sa.select(Category).where(Category.category == cat)
        )

        if category is None and create_if_not_exists:
            category = Category(category=cat)
            db.session.add(category)

        return category

    
class Tag(db.Model):
    id : so.Mapped[int] = so.mapped_column(primary_key=True)
    tag : so.Mapped[str] = so.mapped_column(sa.String(32))
    posts : so.WriteOnlyMapped['Post'] = so.relationship(secondary=post_tags, back_populates='tags')

    def __repr__(self):
        return '<Tag {}>'.format(self.tag)
    
    @property
    def count(self) -> int:
        return db.session.scalar(
            sa.select(sa.func.count()).select_from(self.posts.select().subquery())
        )
    
    @staticmethod
    def find_tag(tagname : str, create_if_not_exists=False):
        tag = db.session.scalar(
            sa.select(Tag).where(Tag.tag == tagname)
        )

        if tag is None and create_if_not_exists:
            tag = Tag(tag=tagname)
            db.session.add(tag)

        return tag
    
class Widget(db.Model):
    id : so.Mapped[int] = so.mapped_column(primary_key=True)
    name : so.Mapped[str] = so.mapped_column(sa.String(32), index=True)
    location: so.Mapped[str] = so.mapped_column(sa.String(32))
    order : so.Mapped[int] = so.mapped_column(sa.Integer, index=True, unique=True)
    is_active : so.Mapped[bool] = so.mapped_column(sa.Boolean, default=False)
    additional_data : so.Mapped[Optional[str]] = so.mapped_column(sa.Text, deferred=True)

    def __repr__(self):
        return '<Widget {}>'.format(self.name)
    
class SocialNetwork(db.Model):
    id : so.Mapped[int] = so.mapped_column(primary_key=True)
    social : so.Mapped[str] = so.mapped_column(sa.String(32), index=True, unique=True)
    url : so.Mapped[str] = so.mapped_column(sa.String(256))
    icon : so.Mapped[str] = so.mapped_column(sa.String(256))
    order : so.Mapped[int] = so.mapped_column(sa.Integer, index=True, unique=True)

    def __repr__(self):
        return '<SocialNetwork {}>'.format(self.social)
