from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from process import scrape, parse, summarize, translate, load_storage, save_storage
import os

app = Flask(__name__)
CORS(app)


@app.route("/api/storage", methods=["GET"])
def get_storage():
    try:
        data = load_storage()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/process", methods=["POST"])
def process_url():
    req = request.get_json()
    url = req.get("url")
    lang = req.get("lang")

    if not url:
        return jsonify({"error": "Missing 'url'"}), 400

    try:
        # Step 1: scrape
        content = scrape(url)
        if content.startswith("Error:"):
            raise ValueError(content)

        # Step 2: parse
        safe_content = parse(content)

        # Step 3: summarize
        summary = summarize(safe_content)

        # Step 4: optional translate
        result = {"url": url, "summary": summary}
        if lang:
            translated = translate(summary, lang)

            # If translate() returns "ASL,<filepath>", store the path in JSON
            if isinstance(translated, str) and translated.startswith("ASL,"):
                _, filepath = translated.split(",", 1)
                filepath = filepath.strip()

                if not os.path.exists(filepath):
                    return jsonify({"error": f"Video file not found: {filepath}"}), 404

                # Store the video path instead of streaming it directly
                result["translation"] = filepath
                result["translation_lang"] = "ASL"

            else:
                result["translation"] = translated
                result["translation_lang"] = lang

        # Step 5: save
        storage = load_storage()
        storage[url] = result
        save_storage(storage)

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Optional: separate endpoint to stream ASL video by path
@app.route("/api/video", methods=["GET"])
def stream_video():
    filepath = request.args.get("path")
    if not filepath or not os.path.exists(filepath):
        return jsonify({"error": "Video file not found"}), 404
    return send_file(filepath, mimetype="video/mp4")


if __name__ == "__main__":
    app.run(port=5000, debug=True)
