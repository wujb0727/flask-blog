import os
from apps import create_app, db
# from apps.models import *
from flask_migrate import Migrate

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
migrate = Migrate(app, db)


# @app.shell_context_processor
# def make_shell_context():
#     return dict(db=db, User=User, Role=Role)


if __name__ == '__main__':
    app.run()
