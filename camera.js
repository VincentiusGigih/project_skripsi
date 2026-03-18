const initCamera = (videoId) => {
    const video = document.getElementById(videoId);
    if (video && navigator.mediaDevices) {
        navigator.mediaDevices.getUserMedia({ video: true })
            .then(stream => { video.srcObject = stream; })
            .catch(err => alert("Akses kamera ditolak!"));
    }
};

const simulateVerification = async (statusId, type) => {
    const status = document.getElementById(statusId);
    const video = document.getElementById('video');
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext('2d').drawImage(video, 0, 0);

    status.innerText = "Memproses Biometrik Wajah...";
    status.style.color = "#3498db";
    
    try {
        const response = await fetch('http://localhost:5000/api/v1/verify-liveness', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                image: canvas.toDataURL('image/jpeg'), 
                type: type 
            })
        });
        const result = await response.json();

        if (result.status === 'success') {
            sessionStorage.setItem('current_user_id', result.user_id);
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