from flask import Flask

from src.blueprints.wallet import walletBlueprint

app = Flask(__name__)

app.register_blueprint(walletBlueprint, url_prefix="/api/v1")