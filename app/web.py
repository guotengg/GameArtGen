from __future__ import annotations

from flask import Flask, jsonify, render_template, request

from app.pipeline import GameArtPipeline


def create_app() -> Flask:
    app = Flask(__name__, template_folder="../templates", static_folder="../static")
    pipeline = GameArtPipeline()

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/generate", methods=["POST"])
    def generate():
        payload = request.get_json(silent=True) or {}
        description = payload.get("description", "")
        negative_prompt = payload.get("negative_prompt")

        try:
            result = pipeline.generate(description, negative_prompt=negative_prompt)
            return jsonify(result)
        except ValueError as err:
            return jsonify({"error": str(err)}), 400
        except Exception as err:
            app.logger.exception("Generate failed")
            return jsonify({"error": f"generation failed: {err}"}), 500

    @app.route("/history", methods=["GET"])
    def history():
        limit = int(request.args.get("limit", 20))
        return jsonify({"items": pipeline.list_history(limit=limit)})

    @app.route("/feedback", methods=["POST"])
    def feedback():
        payload = request.get_json(silent=True) or {}
        prompt = payload.get("enhanced_prompt", "")
        vote = payload.get("vote", "")
        if vote not in {"up", "down"}:
            return jsonify({"error": "vote must be 'up' or 'down'"}), 400
        pipeline.save_feedback(prompt, vote)
        return jsonify({"status": "ok"})

    return app

