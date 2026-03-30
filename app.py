from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import numpy as np
import base64
import sqlite3
import json
import os
import face_recognition
from datetime import datetime

app = Flask(__name__)
CORS(app)

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'payrollface.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    if os.path.exists(DB_PATH):
        return
    conn = get_db_connection()
    try:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nik TEXT NOT NULL UNIQUE,
                nama TEXT NOT NULL,
                role TEXT DEFAULT 'karyawan' CHECK(role IN ('admin','karyawan')),
                gaji_pokok REAL NOT NULL,
                face_encoding TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS attendance_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                tanggal DATE NOT NULL,
                jam_masuk TEXT,
                jam_keluar TEXT,
                status TEXT DEFAULT 'Hadir',
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );
            CREATE TABLE IF NOT EXISTS leaves (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                jenis_cuti TEXT,
                tanggal DATE,
                alasan TEXT,
                attachment TEXT,
                status TEXT DEFAULT 'Pending' CHECK(status IN ('Pending','Approved','Rejected','Cancelled')),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );
            INSERT INTO users (nik, nama, role, gaji_pokok, face_encoding)
            VALUES ('ADMIN001', 'Admin HRD', 'admin', 0, NULL);
        """)
        conn.commit()
    finally:
        conn.close()

init_db()

# 1. API Absensi Biometrik
@app.route('/api/v1/verify-liveness', methods=['POST'])
def verify_absensi():
    data = request.json
    image_data = data.get('image')
    absensi_type = data.get('type')

    try:
        header, encoded = image_data.split(",", 1)
        nparr = np.frombuffer(base64.b64decode(encoded), np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        current_encodings = face_recognition.face_encodings(rgb_img)
        if not current_encodings:
            return jsonify({"status": "failed", "message": "Wajah tidak ditemukan"}), 200

        current_face = current_encodings[0]

        conn = get_db_connection()
        try:
            users = conn.execute("SELECT id, nama, face_encoding FROM users WHERE role = 'karyawan'").fetchall()

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

            now = datetime.now()
            tgl = now.strftime("%Y-%m-%d")
            jam = now.strftime("%H:%M:%S")

            log = conn.execute("SELECT id FROM attendance_logs WHERE user_id = ? AND tanggal = ?", (found_user['id'], tgl)).fetchone()

            if absensi_type == 'Masuk':
                if log:
                    return jsonify({"status": "error", "message": "Sudah absen masuk"}), 200
                conn.execute("INSERT INTO attendance_logs (user_id, tanggal, jam_masuk) VALUES (?, ?, ?)", (found_user['id'], tgl, jam))
            else:
                if not log:
                    return jsonify({"status": "error", "message": "Belum absen masuk"}), 200
                conn.execute("UPDATE attendance_logs SET jam_keluar = ? WHERE id = ?", (jam, log['id']))

            conn.commit()
            return jsonify({"status": "success", "message": f"Halo, {found_user['nama']}", "user_id": found_user['id']})
        finally:
            conn.close()
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

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
        try:
            conn.execute(
                "INSERT INTO users (nik, nama, gaji_pokok, face_encoding, role) VALUES (?, ?, ?, ?, 'karyawan')",
                (data['nik'], data['nama'], data['gaji'], json.dumps(encoding.tolist()))
            )
            conn.commit()
            return jsonify({"status": "success", "message": "Data Karyawan Tersimpan!"})
        finally:
            conn.close()
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# 3. API Ambil Data Personal
@app.route('/api/v1/employee/data/<int:user_id>', methods=['GET'])
def get_employee_data(user_id):
    conn = get_db_connection()
    try:
        user = conn.execute("SELECT nama, nik, gaji_pokok FROM users WHERE id = ?", (user_id,)).fetchone()
        logs = conn.execute("SELECT tanggal, jam_masuk, jam_keluar, status FROM attendance_logs WHERE user_id = ? ORDER BY tanggal DESC", (user_id,)).fetchall()
        return jsonify({
            "user": dict(user) if user else None,
            "logs": [dict(row) for row in logs]
        })
    finally:
        conn.close()

# 4. API Pengajuan Cuti
@app.route('/api/v1/leave/request', methods=['POST'])
def request_leave():
    data = request.json
    try:
        user_id = data.get('user_id') or sessionStorage_fallback(data)
        conn = get_db_connection()
        try:
            conn.execute(
                "INSERT INTO leaves (user_id, jenis_cuti, tanggal, alasan, attachment) VALUES (?, ?, ?, ?, ?)",
                (user_id, data.get('jenis'), data.get('tanggal'), data.get('alasan'), data.get('attachment'))
            )
            conn.commit()
            return jsonify({"status": "success", "message": "Pengajuan cuti berhasil!"})
        finally:
            conn.close()
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

def sessionStorage_fallback(data):
    """If no user_id provided, find by name or default to first karyawan."""
    name = data.get('karyawan')
    conn = get_db_connection()
    try:
        if name:
            user = conn.execute("SELECT id FROM users WHERE nama = ? AND role = 'karyawan'", (name,)).fetchone()
            if user:
                return user['id']
        user = conn.execute("SELECT id FROM users WHERE role = 'karyawan' ORDER BY id LIMIT 1").fetchone()
        return user['id'] if user else None
    finally:
        conn.close()

# 5. API Batalkan Cuti
@app.route('/api/v1/leave/cancel', methods=['POST'])
def cancel_leave():
    data = request.json
    leave_id = data.get('leave_id')
    try:
        conn = get_db_connection()
        try:
            conn.execute("UPDATE leaves SET status = 'Cancelled' WHERE id = ? AND status = 'Pending'", (leave_id,))
            conn.commit()
            return jsonify({"status": "success", "message": "Pengajuan dibatalkan."})
        finally:
            conn.close()
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# 6. API List Cuti (untuk admin approval)
@app.route('/api/v1/leave/list', methods=['GET'])
def list_leaves():
    conn = get_db_connection()
    try:
        rows = conn.execute("""
            SELECT l.id, u.nama as karyawan, l.jenis_cuti, l.tanggal, l.alasan, l.attachment, l.status
            FROM leaves l JOIN users u ON l.user_id = u.id
            ORDER BY l.id DESC
        """).fetchall()
        return jsonify({"leaves": [dict(r) for r in rows]})
    finally:
        conn.close()

# 7. API Approve/Reject Cuti (HRD)
@app.route('/api/v1/leave/approve', methods=['POST'])
def approve_leave():
    data = request.json
    try:
        conn = get_db_connection()
        try:
            conn.execute(
                "UPDATE leaves SET status = ? WHERE id = ? AND status = 'Pending'",
                (data.get('action', 'Approved'), data.get('leave_id'))
            )
            conn.commit()
            return jsonify({"status": "success", "message": f"Cuti {data.get('action', 'Approved')}."})
        finally:
            conn.close()
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# 8. API List Semua Karyawan (untuk admin)
@app.route('/api/v1/employees', methods=['GET'])
def list_employees():
    conn = get_db_connection()
    try:
        rows = conn.execute(
            "SELECT id, nik, nama, gaji_pokok, created_at FROM users WHERE role = 'karyawan' ORDER BY id DESC"
        ).fetchall()
        total = len(rows)
        return jsonify({"total": total, "employees": [dict(r) for r in rows]})
    finally:
        conn.close()

# 9. API Update Data Karyawan
@app.route('/api/v1/employee/update/<int:user_id>', methods=['PUT'])
def update_employee(user_id):
    data = request.json
    try:
        conn = get_db_connection()
        try:
            conn.execute(
                "UPDATE users SET nik = ?, nama = ?, gaji_pokok = ? WHERE id = ? AND role = 'karyawan'",
                (data['nik'], data['nama'], data['gaji_pokok'], user_id)
            )
            conn.commit()
            return jsonify({"status": "success", "message": "Data karyawan berhasil diperbarui."})
        finally:
            conn.close()
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# 10. API Hapus Karyawan
@app.route('/api/v1/employee/delete/<int:user_id>', methods=['DELETE'])
def delete_employee(user_id):
    try:
        conn = get_db_connection()
        try:
            conn.execute("DELETE FROM users WHERE id = ? AND role = 'karyawan'", (user_id,))
            conn.commit()
            return jsonify({"status": "success", "message": "Karyawan berhasil dihapus."})
        finally:
            conn.close()
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# 11. API Riwayat Cuti per Karyawan
@app.route('/api/v1/leave/my/<int:user_id>', methods=['GET'])
def my_leaves(user_id):
    conn = get_db_connection()
    try:
        rows = conn.execute(
            "SELECT id, jenis_cuti, tanggal, alasan, attachment, status FROM leaves WHERE user_id = ? ORDER BY id DESC",
            (user_id,)
        ).fetchall()
        return jsonify({"leaves": [dict(r) for r in rows]})
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
