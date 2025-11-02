from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from process import scrape, parse, summarize, translate, load_storage, save_storage
import os
import json

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:5173"}})

# Path to store uploaded files
UPLOAD_DIR = "uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# --- Existing storage of URL summaries ---
@app.route("/api/storage", methods=["GET"])
def get_storage():
    """Return all processed summaries/videos."""
    try:
        data = load_storage()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- Process a single URL (existing functionality) ---
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
        if content.startswith("Error"):
            raise ValueError(content)

        # Step 2: parse
        safe_content = parse(content)
        if safe_content == "Invalid":
            raise ValueError("Content flagged as unsafe")

        # Step 3: summarize
        summary = summarize(safe_content)

        # Step 4: optional translate
        result = {"url": url, "summary": summary}
        if lang:
            translated = translate(summary, lang, url)
            parts = translated.split(",", 3)  # TYPE, filepath, language, translated_text
            translation_type = parts[0]
            filepath = parts[1].strip()
            translation_lang = parts[2].strip()
            translated_text = parts[3].strip() if len(parts) > 3 else summary

            if translation_type != "ASL":
                result["summary"] = translated_text

            result["translation"] = filepath
            result["translation_lang"] = translation_lang
            result["translation_type"] = translation_type

        # Step 5: save to storage
        storage = load_storage()
        storage[url] = result
        save_storage(storage)

        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- Folder management endpoints ---

@app.route("/api/folders", methods=["GET"])
def get_folders():
    """Return the list of folder names."""
    storage = load_storage()
    return jsonify(list(storage.keys()))

@app.route("/api/create_folder", methods=["POST"])
def create_folder():
    data = request.get_json()
    folder = data.get("folder")
    if not folder:
        return jsonify({"error": "Folder name required"}), 400

    storage = load_storage()
    if folder in storage:
        return jsonify({"error": "Folder already exists"}), 400

    # Initialize folder structure
    storage[folder] = {"urls": [], "files": []}
    save_storage(storage)
    return jsonify({"success": True, "folder": folder})

@app.route("/api/add_url", methods=["POST"])
def add_url():
    data = request.get_json()
    folder = data.get("folder")
    url = data.get("url")
    if not folder or not url:
        return jsonify({"error": "Folder and URL required"}), 400

    storage = load_storage()
    if folder not in storage:
        return jsonify({"error": "Folder does not exist"}), 404

    storage[folder]["urls"].append(url)
    save_storage(storage)
    return jsonify({"success": True, "folder": folder, "url": url})

@app.route("/api/add_files", methods=["POST"])
def add_files():
    folder = request.form.get("folder")
    if not folder:
        return jsonify({"error": "Folder required"}), 400

    storage = load_storage()
    if folder not in storage:
        return jsonify({"error": "Folder does not exist"}), 404

    if "files" not in request.files:
        return jsonify({"error": "No files uploaded"}), 400

    uploaded_files = request.files.getlist("files")
    saved_files = []

    folder_dir = os.path.join(UPLOAD_DIR, folder)
    os.makedirs(folder_dir, exist_ok=True)

    for file in uploaded_files:
        path = os.path.join(folder_dir, file.filename)
        file.save(path)
        saved_files.append({"name": file.filename, "path": path})
        storage[folder]["files"].append({"name": file.filename, "path": path})

    save_storage(storage)
    return jsonify({"success": True, "folder": folder, "files": saved_files})

@app.route("/api/folder_contents", methods=["GET"])
def folder_contents():
    folder = request.args.get("folder")
    if not folder:
        return jsonify({"error": "Folder name required"}), 400

    storage = load_storage()
    if folder not in storage:
        return jsonify({"error": "Folder not found"}), 404

    return jsonify(storage[folder])

# --- Stream ASL videos and audio files ---
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
