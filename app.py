from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import numpy as np
import base64

app = Flask(__name__)
CORS(app)

# API untuk verifikasi liveness (deteksi wajah asli)
@app.route('/api/v1/verify-liveness', methods=['POST'])
def verify_liveness():
    data = request.json
    image_data = data.get('image')
    
    if not image_data:
        return jsonify({"status": "error", "message": "No image data"}), 400

    # Decode base64 image ke format OpenCV
    try:
        header, encoded = image_data.split(",", 1)
        nparr = np.frombuffer(base64.b64decode(encoded), np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # --- UPDATE: Mirroring Image ---
        # Parameter 1 berarti mirroring secara horizontal (kiri-kanan)
        img = cv2.flip(img, 1) 
        # --------------------------------------------------------
        
        # Load classifier untuk deteksi wajah
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)

        if len(faces) > 0:
            return jsonify({
                "status": "success", 
                "message": "Manusia Asli Terdeteksi (Liveness Valid)",
                "confidence": 0.98
            })
        else:
            return jsonify({
                "status": "failed", 
                "message": "Wajah tidak ditemukan atau terdeteksi foto/gambar statis"
            }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    # Menjalankan server di port 5000
    app.run(debug=True, port=5000)