import sqlalchemy as sa
from app import create_app, db
from app.models import User, Post, Widget, Category, Tag

app = create_app()

@app.shell_context_processor
def make_context():
    return {'sa': sa, 'db': db, 'User' : User, 'Post' : Post, 'Widget' : Widget,
            'Category' : Category, 'Tag' : Tag}