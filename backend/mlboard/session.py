import json
import uuid

from flask import Blueprint, Response, request

from .db import get_db

bp = Blueprint("sessions", __name__, url_prefix="/sessions")


@bp.route("/<session_id>", methods=["GET"])
def configure(session_id):
    db = get_db()

    session = db.sessions.find_one({"id": session_id}, {"_id": False})
    if session is not None:
        return Response(json.dumps(session), 200)
    else:
        return Response("invalid session id", 404)


@bp.route("/create", methods=["POST"])
def create():
    new_id = uuid.uuid4().hex[:8]

    db = get_db()
    db.sessions.insert({"id": new_id, "status": 0})

    session = db.sessions.find_one({"id": new_id}, {"_id": False})
    if session is not None:
        return Response(json.dumps(session), 200)
    else:
        return Response("internal error", 500)


@bp.route("/train", methods=["POST"])
def train():
    return "train session"
