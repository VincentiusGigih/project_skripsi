let cameraAvailable = false;

const initCamera = (videoId) => {
    const video = document.getElementById(videoId);
    if (!video) return;

    if (navigator.mediaDevices) {
        navigator.mediaDevices.getUserMedia({ video: true })
            .then(stream => {
                video.srcObject = stream;
                cameraAvailable = true;
            })
            .catch(() => showUploadFallback(videoId));
    } else {
        showUploadFallback(videoId);
    }
};

function showUploadFallback(videoId) {
    const video = document.getElementById(videoId);
    if (!video) return;

    const wrapper = document.createElement('div');
    wrapper.id = videoId + '-fallback';
    wrapper.style.cssText = 'width:100%;aspect-ratio:4/3;border-radius:10px;background:#1a1a2e;display:flex;flex-direction:column;align-items:center;justify-content:center;cursor:pointer;border:2px dashed #3498db;position:relative;overflow:hidden;';

    const preview = document.createElement('img');
    preview.id = videoId + '-preview';
    preview.style.cssText = 'display:none;width:100%;height:100%;object-fit:cover;border-radius:10px;position:absolute;top:0;left:0;';

    const label = document.createElement('div');
    label.id = videoId + '-label';
    label.innerHTML = '<div style="font-size:48px;margin-bottom:10px;">📷</div><div style="color:#3498db;font-size:14px;font-weight:600;">Kamera tidak tersedia</div><div style="color:#95a5a6;font-size:13px;margin-top:6px;">Klik untuk upload foto wajah</div>';
    label.style.textAlign = 'center';

    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'image/*';
    input.id = videoId + '-input';
    input.style.display = 'none';

    input.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (!file) return;
        const reader = new FileReader();
        reader.onload = (ev) => {
            preview.src = ev.target.result;
            preview.style.display = 'block';
            label.innerHTML = '<div style="color:white;font-size:13px;background:rgba(0,0,0,0.5);padding:6px 12px;border-radius:6px;position:absolute;bottom:10px;left:50%;transform:translateX(-50%);white-space:nowrap;">Klik untuk ganti foto</div>';
        };
        reader.readAsDataURL(file);
    });

    wrapper.addEventListener('click', () => input.click());
    wrapper.appendChild(preview);
    wrapper.appendChild(label);
    wrapper.appendChild(input);

    video.style.display = 'none';
    video.parentNode.insertBefore(wrapper, video.nextSibling);
}

function getImageDataUrl(videoId) {
    const video = document.getElementById(videoId);

    if (cameraAvailable && video && video.srcObject) {
        const canvas = document.createElement('canvas');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        canvas.getContext('2d').drawImage(video, 0, 0);
        return canvas.toDataURL('image/jpeg');
    }

    const preview = document.getElementById(videoId + '-preview');
    if (preview && preview.src) {
        return preview.src;
    }

    return null;
}

const simulateVerification = async (statusId, type) => {
    const status = document.getElementById(statusId);
    const imageData = getImageDataUrl('video');

    if (!imageData) {
        status.innerText = "Upload foto wajah terlebih dahulu!";
        status.style.color = "#e74c3c";
        return;
    }

    status.innerText = "Memproses Biometrik Wajah...";
    status.style.color = "#3498db";

    try {
        const response = await fetch('http://localhost:5000/api/v1/verify-liveness', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ image: imageData, type: type })
        });
        const result = await response.json();

        if (result.status === 'success') {
            localStorage.setItem('current_user_id', result.user_id);
            localStorage.setItem('hasAbsen', 'true');
            status.innerHTML = `<span style="color:#27ae60">${result.message}</span>`;
            setTimeout(() => { window.location.href = 'rekap_kehadiran.html'; }, 1500);
        } else {
            status.innerText = "Gagal: " + result.message;
            status.style.color = "#e74c3c";
        }
    } catch (e) {
        status.innerText = "Server Offline!";
    }
};
