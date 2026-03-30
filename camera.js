/**
 * Kamera langsung dari browser (getUserMedia).
 * Frame diambil dari video live — tanpa upload file.
 */

let cameraAvailable = false;

function setHint(elementId, text, color) {
    const el = elementId && document.getElementById(elementId);
    if (el) {
        el.innerText = text;
        if (color) el.style.color = color;
    }
}

/**
 * Polyfill: beberapa browser / konteks hanya punya API lama (webkit / moz).
 * Catatan: di HTTP dengan IP LAN (bukan localhost), Chrome sering tidak menyediakan API kamera sama sekali.
 */
function getUserMediaCompat(constraints) {
    if (navigator.mediaDevices && typeof navigator.mediaDevices.getUserMedia === 'function') {
        return navigator.mediaDevices.getUserMedia(constraints);
    }
    const legacy =
        navigator.getUserMedia ||
        navigator.webkitGetUserMedia ||
        navigator.mozGetUserMedia ||
        navigator.msGetUserMedia;
    if (!legacy) {
        return Promise.reject(new Error('NO_GET_USER_MEDIA'));
    }
    return new Promise((resolve, reject) => {
        legacy.call(navigator, constraints, resolve, reject);
    });
}

function explainCameraBlocked(hintElementId) {
    if (location.protocol === 'file:') {
        setHint(
            hintElementId,
            'Jangan buka file dari folder. Jalankan python app.py lalu buka http://127.0.0.1:5000/',
            '#e74c3c'
        );
        return;
    }

    if (typeof window.isSecureContext === 'boolean' && !window.isSecureContext) {
        const host = location.hostname;
        const isLoopback = host === 'localhost' || host === '127.0.0.1';
        if (!isLoopback && location.protocol === 'http:') {
            setHint(
                hintElementId,
                'Kamera diblokir pada HTTP + IP LAN. Gunakan http://127.0.0.1:5000 di PC, atau USE_HTTPS=1 lalu buka https://IP:5000 (lihat README).',
                '#e74c3c'
            );
            return;
        }
    }

    setHint(
        hintElementId,
        'Browser tidak menyediakan akses kamera. Gunakan Chrome/Edge/Firefox terbaru dan buka http://127.0.0.1:5000 (bukan file://).',
        '#e74c3c'
    );
}

/**
 * @param {string} videoId - id elemen <video>
 * @param {string} [hintElementId] - id elemen untuk pesan status kamera
 */
const initCamera = (videoId, hintElementId) => {
    const video = document.getElementById(videoId);
    if (!video) return;

    cameraAvailable = false;
    setHint(hintElementId, 'Menghubungkan kamera...', '#3498db');

    video.setAttribute('playsinline', '');
    video.setAttribute('muted', '');
    video.muted = true;

    if (location.protocol === 'file:') {
        explainCameraBlocked(hintElementId);
        return;
    }

    const constraints = {
        video: {
            facingMode: { ideal: 'user' },
            width: { ideal: 1280 },
            height: { ideal: 720 },
        },
        audio: false,
    };

    getUserMediaCompat(constraints)
        .then((stream) => {
            video.srcObject = stream;
            cameraAvailable = true;

            const onReady = () => {
                if (video.videoWidth > 0) {
                    setHint(hintElementId, 'Kamera aktif — arahkan wajah ke layar, lalu tekan tombol.', '#27ae60');
                }
            };

            video.onloadedmetadata = () => {
                video.play().catch(() => {});
                onReady();
            };

            video.onresize = onReady;
        })
        .catch((err) => {
            console.error('getUserMedia', err);
            cameraAvailable = false;
            if (err && err.message === 'NO_GET_USER_MEDIA') {
                explainCameraBlocked(hintElementId);
                return;
            }
            let msg = 'Tidak bisa mengakses kamera. ';
            if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
                msg += 'Izinkan akses kamera di pengaturan browser (ikon kunci/gembok di bilah alamat).';
            } else if (err.name === 'NotFoundError') {
                msg += 'Tidak ada kamera terdeteksi.';
            } else if (err.name === 'NotReadableError' || err.name === 'TrackStartError') {
                msg += 'Kamera dipakai aplikasi lain — tutup aplikasi tersebut lalu refresh.';
            } else {
                msg += err.message || String(err);
            }
            setHint(hintElementId, msg, '#e74c3c');
        });
};

function captureFrameFromVideo(video) {
    if (!video || (!video.srcObject && !video.src)) return null;

    const w = video.videoWidth;
    const h = video.videoHeight;
    if (!w || !h) return null;

    const canvas = document.createElement('canvas');
    canvas.width = w;
    canvas.height = h;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0);
    return canvas.toDataURL('image/jpeg', 0.92);
}

function waitForFrame(videoId, maxAttempts = 30) {
    return new Promise((resolve) => {
        const video = document.getElementById(videoId);
        let attempts = 0;

        const tick = () => {
            const data = captureFrameFromVideo(video);
            if (data) {
                resolve(data);
                return;
            }
            attempts += 1;
            if (attempts >= maxAttempts) {
                resolve(null);
                return;
            }
            requestAnimationFrame(tick);
        };
        tick();
    });
}

function getImageDataUrl(videoId) {
    const video = document.getElementById(videoId);
    if (cameraAvailable && video && (video.srcObject || video.src)) {
        return captureFrameFromVideo(video);
    }
    return null;
}

async function getImageDataUrlAsync(videoId) {
    let data = getImageDataUrl(videoId);
    if (data) return data;
    if (!cameraAvailable) return null;
    return await waitForFrame(videoId);
}

const simulateVerification = async (statusId, type) => {
    const status = document.getElementById(statusId);
    const video = document.getElementById('video');

    if (!cameraAvailable || !video || (!video.srcObject && !video.src)) {
        status.innerText =
            'Kamera belum siap. Pastikan membuka http://127.0.0.1:5000 (bukan file://) dan izinkan akses kamera.';
        status.style.color = '#e74c3c';
        return;
    }

    let imageData = captureFrameFromVideo(video);
    if (!imageData) {
        status.innerText = 'Menunggu kamera siap...';
        status.style.color = '#3498db';
        imageData = await waitForFrame('video');
    }

    if (!imageData) {
        status.innerText = 'Gagal mengambil gambar dari kamera. Coba refresh halaman.';
        status.style.color = '#e74c3c';
        return;
    }

    status.innerText = 'Memproses Biometrik Wajah...';
    status.style.color = '#3498db';

    try {
        const response = await fetch('/api/v1/verify-liveness', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ image: imageData, type: type }),
        });
        const result = await response.json();

        if (result.status === 'success') {
            localStorage.setItem('current_user_id', result.user_id);
            localStorage.setItem('hasAbsen', 'true');
            status.innerHTML = `<span style="color:#27ae60">${result.message}</span>`;
            setTimeout(() => {
                window.location.href = 'rekap_kehadiran.html';
            }, 1500);
        } else {
            status.innerText = 'Gagal: ' + result.message;
            status.style.color = '#e74c3c';
        }
    } catch (e) {
        status.innerText = 'Server Offline!';
    }
};
