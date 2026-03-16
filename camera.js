const initCamera = (videoId) => {
    const video = document.getElementById(videoId);
    if (video && navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        navigator.mediaDevices.getUserMedia({ video: true })
            .then(stream => { video.srcObject = stream; })
            .catch(err => { console.error("Kamera Error: ", err); });
    }
};

const simulateVerification = async (statusId, type) => {
    const status = document.getElementById(statusId);
    const video = document.getElementById('video');
    
    if(!video) return;

    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext('2d').drawImage(video, 0, 0);
    const imageData = canvas.toDataURL('image/jpeg');

    status.innerText = "Liveness Detection (Mendeteksi Kedipan)...";
    status.style.color = "#3498db";

    try {
        const response = await fetch('http://localhost:5000/api/v1/verify-liveness', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ image: imageData })
        });

        const result = await response.json();

        if (result.status === 'success') {
            const now = new Date();
            const timeString = now.getHours().toString().padStart(2, '0') + ":" + now.getMinutes().toString().padStart(2, '0');
            const dateString = now.toLocaleDateString('id-ID');

            status.innerText = "Berhasil: " + result.message;
            status.style.color = "#27ae60";

            saveAttendance(dateString, timeString, type);
            localStorage.setItem('hasAbsen', 'true');
            updateNavigation();
        } else {
            status.innerText = "Gagal: " + result.message;
            status.style.color = "#e74c3c";
        }
    } catch (error) {
        status.innerText = "Backend Offline. Gunakan simulasi lokal...";
        status.style.color = "#f39c12";
        // Fallback simulasi jika Flask tidak jalan
        setTimeout(() => {
            localStorage.setItem('hasAbsen', 'true');
            updateNavigation();
            status.innerText = "Verifikasi Berhasil (Simulasi Offline)";
        }, 2000);
    }
};

const saveAttendance = (date, time, type) => {
    let logs = JSON.parse(localStorage.getItem('attendanceLogs')) || [];
    let todayLog = logs.find(l => l.date === date);
    if (!todayLog) {
        todayLog = { date: date, jamMasuk: '-', jamKeluar: '-', status: 'Hadir' };
        logs.push(todayLog);
    }
    if (type === 'Masuk') todayLog.jamMasuk = time;
    else todayLog.jamKeluar = time;
    localStorage.setItem('attendanceLogs', JSON.stringify(logs));
};

const updateNavigation = () => {
    const slipMenu = document.getElementById('menu-slip');
    if (slipMenu && localStorage.getItem('hasAbsen') === 'true') {
        slipMenu.classList.remove('nav-hidden');
    }
};

window.onload = updateNavigation;