from . import login_bp
from . import contact_bp
from . import note_bp
from . import init_bp
from flask import Flask
from .neural_code import predict_class
import threading


def init_app():
    predict_warmup = threading.Thread(target=predict_class, args=("warn up",))
    predict_warmup.start()
    app = Flask(__name__, instance_relative_config=True)
    app.register_blueprint(login_bp.login_bp)
    app.register_blueprint(contact_bp.contact_bp)
    app.register_blueprint(note_bp.note_bp)
    app.register_blueprint(init_bp.init_bp)
    app.before_request_funcs[None] = [init_bp.before_request]
    app.add_url_rule('/', endpoint='index')
    app.config.from_mapping(
        SECRET_KEY=b'gadklnl/dad/;jdisa;l990q3', )
    return app
