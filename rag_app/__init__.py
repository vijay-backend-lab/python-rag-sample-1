from flask import Flask, jsonify, request
from .config import Settings
from .service import ClinicalTrialAssistant

def create_app(settings: Settings | None = None, assistant=None) -> Flask:
    app = Flask(__name__)
    assistant = assistant or ClinicalTrialAssistant.from_settings(settings or Settings.from_env())

    @app.get("/health")
    def health(): return jsonify({"status": "ok"})

    @app.post("/api/v1/query")
    def query():
        body = request.get_json(silent=True) or {}
        question = str(body.get("question", "")).strip()
        if not question: return jsonify({"error": "question is required"}), 400
        try: return jsonify(assistant.answer(question))
        except ValueError as exc: return jsonify({"error": str(exc)}), 422

    @app.post("/api/v1/documents")
    def index_document():
        body = request.get_json(silent=True) or {}
        if not body.get("id") or not body.get("text"): return jsonify({"error": "id and text are required"}), 400
        try:
            assistant.rag.index_document(body)
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 422
        return jsonify({"indexed": body["id"]}), 201
    return app
