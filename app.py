from flask import Flask, request, jsonify
import subprocess, json

app = Flask(__name__)

@app.route("/check", methods=["GET"])
def check():
    image = request.args.get("image")
    if not image:
        return jsonify({"error": "Missing image parameter"}), 400
    try:
        result = subprocess.run(
            ["docker", "manifest", "inspect", image],
            capture_output=True, text=True, check=True
        )
        manifest = json.loads(result.stdout)
        if 'layers' not in manifest:
            return jsonify({"error": "Multi-arch image, specify architecture"}), 400
        total_bytes = sum(layer.get("size", 0) for layer in manifest["layers"])
        return jsonify({
            "size_mb": round(total_bytes / (1024 * 1024), 2),
            "size_gb": round(total_bytes / (1024 * 1024 * 1024), 2)
        })
    except subprocess.CalledProcessError as e:
        return jsonify({"error": e.stderr.strip()}), 500

@app.route("/")
def index():
    return app.send_static_file("index.html")

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))  # Render expone este puerto
    app.run(host="0.0.0.0", port=port)
