from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from process import scrape, parse, summarize, translate, load_storage, save_storage
import os

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:5173"}})

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
        print(f"Scraping URL: {url}")
        content = scrape(url)
        if content.startswith("Error"):
            raise ValueError(content)

        # Step 2: parse
        print("Parsing content...")
        safe_content = parse(content)
        if safe_content == "Invalid":
            raise ValueError("Content was flagged as unsafe")

        # Step 3: summarize
        print("Summarizing...")
        summary = summarize(safe_content)

        # Step 4: optional translate
        result = {"url": url, "summary": summary}
        if lang:
            print(f"Translating to {lang}...")
            translated = translate(summary, lang, url)

            # Parse the response: "TYPE,filepath,language,translated_text"
            parts = translated.split(",", 3)  # Split into max 4 parts
            translation_type = parts[0]
            filepath = parts[1].strip()
            translation_lang = parts[2].strip()
            translated_text = parts[3].strip() if len(parts) > 3 else summary

            if not os.path.exists(filepath):
                return jsonify({"error": f"File not found: {filepath}"}), 404

            # Replace summary with translated version for non-ASL translations
            if translation_type != "ASL":
                result["summary"] = translated_text

            # Add all translation info to result
            result["translation"] = filepath
            result["translation_lang"] = translation_lang
            result["translation_type"] = translation_type
            
            print(f"Translation saved: {filepath} ({translation_lang})")

        # Step 5: save
        storage = load_storage()
        storage[url] = result
        save_storage(storage)

        print("Success!")
        print(f"Returning result: {result}")
        return jsonify(result)

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Optional: separate endpoint to stream ASL video by path
@app.route("/api/video", methods=["GET"])
def stream_video():
    filepath = request.args.get("path")
    if not filepath or not os.path.exists(filepath):
        return jsonify({"error": "Video file not found"}), 404
    return send_file(filepath, mimetype="video/mp4")


@app.route("/api/audio", methods=["GET"])
def stream_audio():
    filepath = request.args.get("path")
    if not filepath or not os.path.exists(filepath):
        return jsonify({"error": "Audio file not found"}), 404
    return send_file(filepath, mimetype="audio/mpeg")


if __name__ == "__main__":
    app.run(port=5000, debug=True)
