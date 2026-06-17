from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Central extensions instance (imported by models / blueprints)
db = SQLAlchemy()
login_manager = LoginManager()

# Configure LoginManager defaults here so it is consistent across modules.
login_manager.login_view = "auth.login"


