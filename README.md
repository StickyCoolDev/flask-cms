# Flask CMS

A simple flask CMS

## How to use
install UV:
```
pip install uv
```

Setup venv:
```
uv venv
source .venv/bin/activate
```

install all dependencies:

```
uv sync # ( recomended )

# or 

uv pip install -r requirements.txt
```

Setup **Database**:
```
flask db upgrade

# or 
uv run flask db upgrade
```

Run :
```
export FLASK_APP=flask_cms.py
export FLASK_ENV=development
flask run 
# or 
uv run flask run
```
