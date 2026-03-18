from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import numpy as np
import base64
import mysql.connector
import json
import face_recognition

app = Flask(__name__)
CORS(app)

# Konfigurasi Database
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'payrollface_db'
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

# 1. API Absensi Biometrik
@app.route('/api/v1/verify-liveness', methods=['POST'])
def verify_absensi():
    data = request.json
    image_data = data.get('image')
    absensi_type = data.get('type')
    
    try:
        # Decode Image dari Base64
        header, encoded = image_data.split(",", 1)
        nparr = np.frombuffer(base64.b64decode(encoded), np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Cari encoding wajah dari kamera
        current_encodings = face_recognition.face_encodings(rgb_img)
        if not current_encodings:
            return jsonify({"status": "failed", "message": "Wajah tidak ditemukan"}), 200
        
        current_face = current_encodings[0]

        # Cocokkan dengan semua user di database
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, nama, face_encoding FROM users WHERE role = 'karyawan'")
        users = cursor.fetchall()
        
        found_user = None
        for u in users:
            if u['face_encoding']:
                db_encoding = np.array(json.loads(u['face_encoding']))
                matches = face_recognition.compare_faces([db_encoding], current_face, tolerance=0.5)
                if matches[0]:
                    found_user = u
                    break
        
        if not found_user:
            return jsonify({"status": "failed", "message": "Wajah tidak terdaftar"}), 200

        # Logika Catat Kehadiran
        from datetime import datetime
        now = datetime.now()
        tgl = now.date()
        jam = now.strftime("%H:%M:%S")

        cursor.execute("SELECT id FROM attendance_logs WHERE user_id = %s AND tanggal = %s", (found_user['id'], tgl))
        log = cursor.fetchone()

        if absensi_type == 'Masuk':
            if log: return jsonify({"status": "error", "message": "Sudah absen masuk"}), 200
            cursor.execute("INSERT INTO attendance_logs (user_id, tanggal, jam_masuk) VALUES (%s, %s, %s)", (found_user['id'], tgl, jam))
        else:
            if not log: return jsonify({"status": "error", "message": "Belum absen masuk"}), 200
            cursor.execute("UPDATE attendance_logs SET jam_keluar = %s WHERE id = %s", (jam, log['id']))

        conn.commit()
        return jsonify({"status": "success", "message": f"Halo, {found_user['nama']}", "user_id": found_user['id']})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        if 'conn' in locals(): conn.close()

# 2. API Enrollment (HRD Daftarkan Karyawan)
@app.route('/api/v1/face/register', methods=['POST'])
def enroll_user():
    data = request.json
    try:
        header, encoded = data['image'].split(",", 1)
        nparr = np.frombuffer(base64.b64decode(encoded), np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encoding = face_recognition.face_encodings(rgb_img)[0]
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (nik, nama, gaji_pokok, face_encoding, role) VALUES (%s, %s, %s, %s, 'karyawan')",
                       (data['nik'], data['nama'], data['gaji'], json.dumps(encoding.tolist())))
        conn.commit()
        return jsonify({"status": "success", "message": "Data Karyawan Tersimpan!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# 3. API Ambil Data Personal
@app.route('/api/v1/employee/data/<int:user_id>', methods=['GET'])
def get_employee_data(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT nama, nik, gaji_pokok FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.execute("SELECT tanggal, jam_masuk, jam_keluar, status FROM attendance_logs WHERE user_id = %s ORDER BY tanggal DESC", (user_id,))
    logs = cursor.fetchall()
    conn.close()
    return jsonify({"user": user, "logs": logs})

if __name__ == '__main__':
    app.run(debug=True, port=5000)