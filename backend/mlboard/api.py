import json
import uuid
import datetime

import pandas as pd
import pymongo
import pickle
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

    cursor = db.sessions.find({}).sort([("created_at", pymongo.DESCENDING)])
    sessions = []
    for session in cursor:
        sessions.append(
            {
                "id": session["id"],
                "status": session["status"],
                "created_at": session["created_at"].isoformat(),
                "dim_reduction": session["dim_reduction"],
                "classifier": session["classifier"],
                "data_filename": session["data_filename"],
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
        "dim_reduction": session["dim_reduction"],
        "classifier": session["classifier"],
        "data_filename": session["data_filename"],
    }
    return Response(json.dumps(response), 200)


@bp.route("/create", methods=["POST"])
def create_session():
    new_id = uuid.uuid4().hex[:8]

    db = get_db()
    db.sessions.insert_one(
        {
            "id": new_id,
            "status": 0,
            "created_at": datetime.datetime.utcnow(),
            "dim_reduction": "",
            "classifier": "",
            "data_object": "",
            "data_filename": "",
        }
    )

    return get_session(new_id)


@bp.route("/train", methods=["POST"])
def train_session():
    # Check params part
    if "params" not in request.form:
        return Response("no params part", 400)
    try:
        params = json.loads(request.form["params"])
    except ValueError as e:
        return Response("invalid params", 400)

    # Check session
    db = get_db()
    if "id" not in params:
        return Response("no session id", 400)
    session = db.sessions.find_one({"id": params["id"]})
    if session is None:
        return Response("invalid session id", 400)

    # Check train params
    if "dim_reduction" in params and params["dim_reduction"] in dim_reductions:
        dim_reduction = dim_reductions[params["dim_reduction"]]
    else:
        return Response("invalid params", 400)
    if "classifier" in params and params["classifier"] in classifiers:
        classifier = classifiers[params["classifier"]]
    else:
        return Response("invalid params", 400)

    # Load dataset file
    if "data" in request.files:
        file = request.files["data"]
        try:
            data = pd.read_csv(file, sep=";")
        except pd.errors.ParserError as e:
            return Response("data is not a valid csv with ';' separator", 400)
        data_filename = file.filename
    else:
        if session["status"] == 1:
            data = pickle.loads(session["data_object"])
            data_filename = session["data_filename"]
        else:
            return Response("no data file part", 400)

    # Train session
    X = data.iloc[:, 0:-1]
    y = data.iloc[:, -1:].values.ravel()
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33)
    pipeline = Pipeline(
        [("dim_reduction", dim_reduction), ("classification", classifier)]
    )
    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)
    print(classification_report(y_test, y_pred))

    # Save session params and file
    db.sessions.update_one(
        {"id": params["id"]},
        {
            "$set": {
                "status": 1,
                "dim_reduction": params["dim_reduction"],
                "classifier": params["classifier"],
                "data_object": pickle.dumps(data),
                "data_filenime": data_filename,
            }
        },
        upsert=False,
    )

    return "train session"
