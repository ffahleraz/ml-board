from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

# from flaskr.db import get_db

bp = Blueprint("auth", __name__, url_prefix="/session")


@bp.route("/create", methods=["GET"])
def create():
    return "create session"


@bp.route("/configure", methods=["GET"])
def configure():
    return "configure session"

