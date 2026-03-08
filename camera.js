const initCamera = (videoId) => {
    const video = document.getElementById(videoId);
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        navigator.mediaDevices.getUserMedia({ video: true })
            .then(stream => { video.srcObject = stream; })
            .catch(err => { console.error("Error Kamera: ", err); });
    }
};

const simulateVerification = (statusId) => {
    const status = document.getElementById(statusId);
    status.innerText = "Mendeteksi Wajah...";
    setTimeout(() => {
        status.innerText = "Liveness Check: Silakan Berkedip...";
        setTimeout(() => {
            status.innerText = "Verifikasi Berhasil!";
            status.style.color = "#27ae60";
        }, 2000);
    }, 2000);
};