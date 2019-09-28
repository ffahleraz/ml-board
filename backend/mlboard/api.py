import json
import uuid
import datetime

import pandas as pd
from flask import Blueprint, Response, request
from sklearn.ensemble import RandomForestClassifier
from sklearn.decomposition import PCA
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

from .db import get_db

bp = Blueprint("api", __name__, url_prefix="/api")

dim_reduce_methods = {"pca": PCA}
classifiers = {"random_forest": RandomForestClassifier}


@bp.route("/sessions", methods=["GET"])
def get_all_sessions():
    db = get_db()

    cursor = db.sessions.find({})
    sessions = []
    for session in cursor:
        sessions.append(
            {
                "id": session["id"],
                "status": session["status"],
                "created_at": session["created_at"].isoformat(),
            }
        )

    response = {"sessions": sessions}
    return Response(json.dumps(response), 200)


@bp.route("/sessions/<session_id>", methods=["GET"])
def get_session(session_id):
    db = get_db()

    session = db.sessions.find_one({"id": session_id})
    if session is None:
        return Response("invalid session id", 404)

    response = {
        "id": session["id"],
        "status": session["status"],
        "created_at": session["created_at"].isoformat(),
    }
    return Response(json.dumps(response), 200)


@bp.route("/create", methods=["POST"])
def create_session():
    new_id = uuid.uuid4().hex[:8]

    db = get_db()
    db.sessions.insert_one(
        {"id": new_id, "status": 0, "created_at": datetime.datetime.utcnow()}
    )

    session = db.sessions.find_one({"id": new_id}, {"_id": False})
    if session is None:
        return Response("internal error", 500)

    return get_session(new_id)


@bp.route("/train", methods=["POST"])
def train_session():
    if "data" not in request.files:
        return Response("no data file part", 400)
    file = request.files["data"]
    if file.filename == "":
        return Response("data file not selected", 400)

    if "config" not in request.form:
        return Response("no config part", 400)

    try:
        config = json.loads(request.form["config"])
    except ValueError as e:
        return Response("invalid config", 400)

    if "dim_reduce" in config and config["dim_reduce"] in dim_reduce_methods:
        dim_reduce_method = dim_reduce_methods[config["dim_reduce"]]
    else:
        return Response("invalid config", 400)
    if "classifier" in config and config["classifier"] in classifiers:
        classifier = classifiers[config["classifier"]]
    else:
        return Response("invalid config", 400)

    data = pd.read_csv(file, sep=";")
    X = data.iloc[:, 0:-1]
    y = data.iloc[:, -1:].values.ravel()
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33)

    pipeline = Pipeline(
        [("feature_selection", dim_reduce_method()), ("classification", classifier())]
    )
    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)
    print(classification_report(y_test, y_pred))

    return "train session"
