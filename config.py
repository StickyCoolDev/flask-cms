import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'super-secret-code-do-not-steal'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', '') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    PER_PAGE = int(os.environ.get('PER_PAGE') or 3)
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')
    RESUME_LENGTH = int(os.environ.get('RESUME_LENGTH') or 100) 
    RECAPTCHA_PUBLIC_KEY = os.environ.get('RECAPTCHA_PUBLIC_KEY')
    RECAPTCHA_PRIVATE_KEY= os.environ.get('RECAPTCHA_PRIVATE_KEY')