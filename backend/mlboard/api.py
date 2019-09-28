import json
import uuid
import datetime

import pandas as pd
from flask import Blueprint, Response, request
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.decomposition import PCA, NMF
from sklearn.feature_selection import SelectKBest, chi2
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

from .db import get_db

bp = Blueprint("api", __name__, url_prefix="/api")

dim_reductions = {"pca": PCA(), "nmf": NMF(), "chi2": SelectKBest(chi2)}
classifiers = {
    "random_forest": RandomForestClassifier(),
    "ada_boost": AdaBoostClassifier(),
    "naive_bayes": GaussianNB(),
}


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
                "dim_reduction": "",
                "classifier": "",
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

    if "dim_reduction" in config and config["dim_reduction"] in dim_reductions:
        dim_reduction = dim_reductions[config["dim_reduction"]]
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
        [("dim_reduction", dim_reduction), ("classification", classifier)]
    )
    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)
    print(classification_report(y_test, y_pred))

    return "train session"
