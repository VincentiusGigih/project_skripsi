// Inisialisasi Kamera
const initCamera = (videoId) => {
    const video = document.getElementById(videoId);
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        navigator.mediaDevices.getUserMedia({ video: true })
            .then(stream => { video.srcObject = stream; })
            .catch(err => { console.error("Error Kamera: ", err); });
    }
};

// Simulasi Verifikasi di Dashboard (Munculkan Menu Slip Gaji)
const simulateVerification = (statusId) => {
    const status = document.getElementById(statusId);
    status.innerText = "Mendeteksi Wajah...";
    setTimeout(() => {
        status.innerText = "Liveness Check: Silakan Berkedip...";
        setTimeout(() => {
            status.innerText = "Verifikasi Berhasil!";
            status.style.color = "#27ae60";
            // Munculkan menu setelah sukses
            const menu = document.getElementById('menu-slip-gaji');
            if(menu) menu.classList.remove('hidden');
        }, 2000);
    }, 2000);
};

// Fungsi Preview untuk Upload Foto
const handleFilePreview = (input, previewId) => {
    const file = input.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            const preview = document.getElementById(previewId);
            preview.innerHTML = `<img src="${e.target.result}" alt="Preview">`;
        };
        reader.readAsDataURL(file);
    }
};