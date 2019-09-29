import json
import uuid
import datetime
import io

import pandas as pd
import pymongo
import joblib
import pickle
from flask import Blueprint, Response, request, send_file
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.decomposition import PCA, NMF
from sklearn.feature_selection import SelectKBest, chi2
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

from .db import get_db
from .helpers import generate_normalized_confusion_matrix

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
                "report": session["report"],
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
        "report": session["report"],
    }
    return Response(json.dumps(response), 200)


@bp.route("/sessions/<session_id>/model", methods=["GET"])
def get_session_model(session_id):
    db = get_db()

    session = db.sessions.find_one({"id": session_id})
    if session is None:
        return Response("invalid session id", 404)

    model_stream = io.BytesIO()
    model_stream.write(session["model"])
    model_stream.seek(0)

    return send_file(
        model_stream,
        mimetype="application/octet-stream",
        attachment_filename="model.pkl",
        as_attachment=True,
        conditional=False,
    )


@bp.route("/sessions/<session_id>/conf_mat", methods=["GET"])
def get_session_conf_mat(session_id):
    db = get_db()

    session = db.sessions.find_one({"id": session_id})
    if session is None:
        return Response("invalid session id", 404)

    image_stream = io.BytesIO()
    image_stream.write(session["confusion_matrix"])
    image_stream.seek(0)

    return send_file(image_stream, mimetype="image/jpeg")


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
            "report": None,
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
    if "session_id" not in params:
        return Response("no session id", 400)
    session = db.sessions.find_one({"id": params["session_id"]})
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

    model_stream = io.BytesIO()
    joblib.dump(pipeline, model_stream)

    confusion_matrix = generate_normalized_confusion_matrix(y_test, y_pred)
    metrics = classification_report(y_test, y_pred, output_dict=True)

    macro_avg = metrics.pop("macro avg")
    weighted_avg = metrics.pop("weighted avg")
    report = {
        "accuracy": metrics.pop("accuracy"),
        "macro_avg": {
            "precision": macro_avg["precision"],
            "recall": macro_avg["recall"],
            "f1_score": macro_avg["f1-score"],
            "support": macro_avg["support"],
        },
        "weighted_avg": {
            "precision": weighted_avg["precision"],
            "recall": weighted_avg["recall"],
            "f1_score": weighted_avg["f1-score"],
            "support": weighted_avg["support"],
        },
        "by_class": [],
    }

    for class_name in metrics.keys():
        entry = {"class": class_name}
        for metric_name in metrics[class_name].keys():
            entry[metric_name] = metrics[class_name][metric_name]
        report["by_class"].append(
            {
                "class_name": class_name,
                "precision": entry["precision"],
                "recall": entry["recall"],
                "f1_score": entry["f1-score"],
                "support": entry["support"],
            }
        )

    # Save session params and file
    db.sessions.update_one(
        {"id": params["session_id"]},
        {
            "$set": {
                "status": 1,
                "dim_reduction": params["dim_reduction"],
                "classifier": params["classifier"],
                "data_object": pickle.dumps(data),
                "data_filename": data_filename,
                "report": report,
                "confusion_matrix": confusion_matrix,
                "model": model_stream.getvalue(),
            }
        },
        upsert=False,
    )

    response = {"report": report}
    return Response(json.dumps(response), 200)
