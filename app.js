// TikTok Live AI Avatar Application
class TikTokLiveAI {
    constructor() {
        this.socket = null;
        this.isStreaming = false;
        this.mediaStream = null;
        this.selectedAvatar = 'default';
        this.chatQueue = [];
        this.streamDuration = 0;
        this.streamTimer = null;
        
        this.init();
    }

    init() {
        // Initialize Socket.IO connection
        this.socket = io('http://localhost:3000');
        
        // Setup event listeners
        this.setupEventListeners();
        this.setupSocketListeners();
        
        // Initialize media devices
        this.initializeMediaDevices();
        
        // Initialize product manager
        productManager = new ProductManager(this);
    }

    setupEventListeners() {
        // TikTok Connection
        document.getElementById('connectTikTok').addEventListener('click', () => {
            this.connectToTikTok();
        });

        // Avatar Selection
        document.querySelectorAll('.avatar-card').forEach(card => {
            card.addEventListener('click', (e) => {
                const avatarType = card.dataset.avatar;
                if (avatarType === 'custom') {
                    // Open upload modal for custom avatar
                    document.getElementById('uploadModal').classList.add('active');
                } else {
                    // Select predefined avatar
                    this.selectAvatar(avatarType);
                }
            });
        });

        // Control Sliders
        document.getElementById('speechSpeed').addEventListener('input', (e) => {
            document.querySelector('#speechSpeed + .value-display').textContent = e.target.value + 'x';
        });

        document.getElementById('pitch').addEventListener('input', (e) => {
            document.querySelector('#pitch + .value-display').textContent = e.target.value;
        });

        document.getElementById('gestureIntensity').addEventListener('input', (e) => {
            document.querySelector('#gestureIntensity + .value-display').textContent = e.target.value + '%';
        });

        // Chat Queue
        document.getElementById('addToQueue').addEventListener('click', () => {
            this.addToQueue();
        });

        // Video Controls
        document.getElementById('toggleCamera').addEventListener('click', () => {
            this.toggleCamera();
        });

        document.getElementById('toggleMic').addEventListener('click', () => {
            this.toggleMic();
        });

        document.getElementById('toggleAvatar').addEventListener('click', () => {
            this.toggleAvatar();
        });

        document.getElementById('shareScreen').addEventListener('click', () => {
            this.shareScreen();
        });

        // Stream Controls
        document.getElementById('startStream').addEventListener('click', () => {
            this.startStream();
        });

        document.getElementById('stopStream').addEventListener('click', () => {
            this.stopStream();
        });

        // Chat
        document.getElementById('sendChat').addEventListener('click', () => {
            this.sendChat();
        });

        document.getElementById('chatInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendChat();
            }
        });

        // Avatar Upload
        document.querySelector('.avatar-card[data-avatar="custom"]').addEventListener('click', () => {
            document.getElementById('uploadModal').classList.add('active');
        });
    }

    setupSocketListeners() {
        this.socket.on('connect', () => {
            console.log('Connected to server');
        });

        this.socket.on('chat', (data) => {
            this.displayChat(data);
        });

        this.socket.on('gift', (data) => {
            this.displayGift(data);
        });

        this.socket.on('viewer_count', (count) => {
            document.getElementById('viewerCount').textContent = count;
        });

        this.socket.on('like', (count) => {
            document.getElementById('likeCount').textContent = count;
        });

        this.socket.on('comment_count', (count) => {
            document.getElementById('commentCount').textContent = count;
        });
        
        this.socket.on('new_order', (orderData) => {
            if (productManager) {
                productManager.addOrder(orderData);
            }
        });
    }

    async initializeMediaDevices() {
        // Initialize with AI Avatar by default (no camera needed)
        this.useAvatar = true;
        this.startAvatarStream();
        
        // Initialize audio only
        try {
            this.mediaStream = await navigator.mediaDevices.getUserMedia({
                audio: true
            });
        } catch (error) {
            console.log('Audio not available:', error);
        }
    }
    
    startAvatarStream() {
        const canvas = document.getElementById('avatarCanvas');
        const video = document.getElementById('avatarVideo');
        const overlay = document.getElementById('statusOverlay');
        
        // Show canvas, hide video
        canvas.style.display = 'block';
        video.style.display = 'none';
        
        const ctx = canvas.getContext('2d');
        // Portrait mode for TikTok (9:16 ratio)
        canvas.width = 1080;
        canvas.height = 1920;
        
        // Show loading text on canvas
        ctx.fillStyle = '#1e1e1e';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.fillStyle = '#25f4ee';
        ctx.font = '30px Arial';
        ctx.textAlign = 'center';
        ctx.fillText('👤 Loading Realistic Human Avatar...', canvas.width/2, canvas.height/2);
        ctx.font = '20px Arial';
        ctx.fillText('Using real photos for authentic look', canvas.width/2, canvas.height/2 + 40);
        
        // Start fetching avatar frames
        let frameCount = 0;
        this.avatarFrameInterval = setInterval(() => {
            this.fetchAvatarFrame(ctx);
            frameCount++;
            if (frameCount === 3) {
                // Hide overlay after a few frames loaded
                overlay.style.display = 'none';
            }
        }, 33); // ~30 FPS
        
        setTimeout(() => {
            this.showNotification('✅ Realistic Human Avatar aktif! Menggunakan foto asli!', 'success');
        }, 1000);
    }
    
    stopAvatarStream() {
        if (this.avatarFrameInterval) {
            clearInterval(this.avatarFrameInterval);
        }
    }
    
    async fetchAvatarFrame(ctx) {
        try {
            const gestureIntensity = document.getElementById('gestureIntensity').value;
            const isSpeaking = this.isSpeaking || false;
            const currentText = this.currentSpeakingText || '';
            
            const response = await fetch(`http://localhost:5000/api/frame/avatar_stream?gesture=${gestureIntensity}&speaking=${isSpeaking}&text=${encodeURIComponent(currentText)}&t=${Date.now()}`);
            
            if (response.ok) {
                const blob = await response.blob();
                const img = await createImageBitmap(blob);
                ctx.drawImage(img, 0, 0, ctx.canvas.width, ctx.canvas.height);
                
                // Update status to show interactive avatar is working
                const overlay = document.getElementById('statusOverlay');
                if (overlay) {
                    overlay.style.display = 'none';
                }
            }
        } catch (error) {
            console.log('Fetching interactive avatar frame...');
        }
    }
    
    async startCameraStream() {
        try {
            this.cameraStream = await navigator.mediaDevices.getUserMedia({
                video: true,
                audio: false
            });
            
            const video = document.getElementById('avatarVideo');
            const canvas = document.getElementById('avatarCanvas');
            
            video.srcObject = this.cameraStream;
            video.style.display = 'block';
            canvas.style.display = 'none';
            
            this.showNotification('Kamera aktif', 'success');
        } catch (error) {
            console.error('Error accessing camera:', error);
            this.showNotification('Gagal mengakses kamera', 'error');
        }
    }
    
    stopCameraStream() {
        if (this.cameraStream) {
            this.cameraStream.getTracks().forEach(track => track.stop());
            this.cameraStream = null;
        }
    }

    connectToTikTok() {
        // Simulate TikTok OAuth flow
        const clientKey = 'YOUR_TIKTOK_CLIENT_KEY';
        const redirectUri = encodeURIComponent('http://localhost:3000/auth/callback');
        const scope = 'user.info.basic,video.upload,live.room.manage';
        
        const authUrl = `https://www.tiktok.com/auth/authorize/?client_key=${clientKey}&scope=${scope}&response_type=code&redirect_uri=${redirectUri}`;
        
        // Open auth window
        const authWindow = window.open(authUrl, 'TikTok Auth', 'width=600,height=700');
        
        // Listen for auth callback
        window.addEventListener('message', (event) => {
            if (event.data.type === 'tiktok-auth') {
                this.handleTikTokAuth(event.data);
                authWindow.close();
            }
        });
    }

    handleTikTokAuth(data) {
        // Store auth data
        localStorage.setItem('tiktok_token', data.token);
        localStorage.setItem('tiktok_user', JSON.stringify(data.user));
        
        // Update UI
        document.getElementById('connectTikTok').style.display = 'none';
        document.getElementById('userProfile').style.display = 'flex';
        document.getElementById('userAvatar').src = data.user.avatar;
        document.getElementById('username').textContent = data.user.username;
        
        this.showNotification('Berhasil terhubung ke TikTok!', 'success');
    }

    async selectAvatar(avatarType) {
        // Update UI
        document.querySelectorAll('.avatar-card').forEach(card => {
            card.classList.remove('active');
        });
        document.querySelector(`[data-avatar="${avatarType}"]`).classList.add('active');
        
        this.selectedAvatar = avatarType;
        
        // Notify backend to change avatar
        try {
            await fetch('http://localhost:5000/api/avatar/change', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ avatar: avatarType })
            });
        } catch (error) {
            console.error('Error changing avatar:', error);
        }
        
        // Emit to server
        this.socket.emit('avatar_change', { avatar: avatarType });
        
        this.showNotification(`Avatar ${avatarType} dipilih`, 'success');
    }

    addToQueue() {
        const scriptInput = document.getElementById('scriptInput');
        const text = scriptInput.value.trim();
        
        if (!text) {
            this.showNotification('Masukkan script terlebih dahulu', 'warning');
            return;
        }
        
        this.chatQueue.push({
            id: Date.now(),
            text: text
        });
        
        this.updateQueueDisplay();
        scriptInput.value = '';
        
        // Process queue if streaming
        if (this.isStreaming) {
            this.processQueue();
        }
    }

    updateQueueDisplay() {
        const queueList = document.getElementById('queueList');
        
        if (this.chatQueue.length === 0) {
            queueList.innerHTML = '<div class="queue-empty">Belum ada chat di queue</div>';
            return;
        }
        
        queueList.innerHTML = this.chatQueue.map(item => `
            <div class="queue-item" data-id="${item.id}">
                <span class="text">${item.text}</span>
                <button onclick="app.removeFromQueue(${item.id})">Hapus</button>
            </div>
        `).join('');
    }

    removeFromQueue(id) {
        this.chatQueue = this.chatQueue.filter(item => item.id !== id);
        this.updateQueueDisplay();
    }

    processQueue() {
        if (this.chatQueue.length === 0) return;
        
        const item = this.chatQueue.shift();
        this.updateQueueDisplay();
        
        // Send to AI Avatar for speech
        this.socket.emit('speak', {
            text: item.text,
            avatar: this.selectedAvatar,
            voice: document.getElementById('voiceType').value,
            speed: document.getElementById('speechSpeed').value,
            pitch: document.getElementById('pitch').value
        });
        
        // Process next item after delay
        setTimeout(() => {
            if (this.isStreaming) {
                this.processQueue();
            }
        }, 5000);
    }

    toggleCamera() {
        const btn = document.getElementById('toggleCamera');
        
        if (!this.cameraStream) {
            // Turn camera ON - switch from avatar to camera
            btn.classList.add('active');
            btn.innerHTML = '<i class="fas fa-video"></i>';
            this.useAvatar = false;
            this.stopAvatarStream();
            this.startCameraStream();
            
            // Update avatar button
            document.getElementById('toggleAvatar').classList.remove('active');
            this.showNotification('Kamera real aktif', 'info');
        } else {
            // Turn camera OFF - switch to avatar
            btn.classList.remove('active');
            btn.innerHTML = '<i class="fas fa-video-slash"></i>';
            this.stopCameraStream();
            this.useAvatar = true;
            this.startAvatarStream();
            
            // Update avatar button
            document.getElementById('toggleAvatar').classList.add('active');
            this.showNotification('Kembali ke AI Avatar', 'info');
        }
    }

    toggleMic() {
        const btn = document.getElementById('toggleMic');
        const audioTrack = this.mediaStream?.getAudioTracks()[0];
        
        if (audioTrack) {
            audioTrack.enabled = !audioTrack.enabled;
            btn.classList.toggle('active');
            btn.innerHTML = audioTrack.enabled 
                ? '<i class="fas fa-microphone"></i>' 
                : '<i class="fas fa-microphone-slash"></i>';
        }
    }

    toggleAvatar() {
        const btn = document.getElementById('toggleAvatar');
        this.useAvatar = !this.useAvatar;
        
        if (this.useAvatar) {
            // Switch to AI Avatar
            btn.classList.add('active');
            this.stopCameraStream();
            this.startAvatarStream();
        } else {
            // Switch to Camera
            btn.classList.remove('active');
            this.stopAvatarStream();
            this.startCameraStream();
        }
        
        this.socket.emit('toggle_avatar', { enabled: this.useAvatar });
    }

    async shareScreen() {
        try {
            const screenStream = await navigator.mediaDevices.getDisplayMedia({
                video: true
            });
            
            document.getElementById('avatarVideo').srcObject = screenStream;
            this.showNotification('Screen sharing dimulai', 'success');
        } catch (error) {
            console.error('Error sharing screen:', error);
            this.showNotification('Gagal share screen', 'error');
        }
    }

    startStream() {
        if (!this.isStreaming) {
            this.isStreaming = true;
            
            // Update UI
            document.getElementById('startStream').style.display = 'none';
            document.getElementById('stopStream').style.display = 'inline-flex';
            document.getElementById('statusOverlay').classList.add('streaming');
            
            // Get stream settings
            const settings = {
                quality: document.getElementById('streamQuality').value,
                bitrate: document.getElementById('bitrate').value,
                fps: document.getElementById('fps').value,
                background: document.getElementById('background').value,
                avatar: this.selectedAvatar
            };
            
            // Start streaming
            this.socket.emit('start_stream', settings);
            
            // Start timer
            this.streamDuration = 0;
            this.streamTimer = setInterval(() => {
                this.streamDuration++;
                this.updateDuration();
            }, 1000);
            
            // Start processing queue
            this.processQueue();
            
            this.showNotification('Streaming dimulai!', 'success');
        }
    }

    stopStream() {
        if (this.isStreaming) {
            this.isStreaming = false;
            
            // Update UI
            document.getElementById('startStream').style.display = 'inline-flex';
            document.getElementById('stopStream').style.display = 'none';
            document.getElementById('statusOverlay').classList.remove('streaming');
            
            // Stop streaming
            this.socket.emit('stop_stream');
            
            // Stop timer
            clearInterval(this.streamTimer);
            
            this.showNotification('Streaming dihentikan', 'info');
        }
    }

    updateDuration() {
        const hours = Math.floor(this.streamDuration / 3600);
        const minutes = Math.floor((this.streamDuration % 3600) / 60);
        const seconds = this.streamDuration % 60;
        
        const formatted = [hours, minutes, seconds]
            .map(v => v.toString().padStart(2, '0'))
            .join(':');
        
        document.getElementById('duration').textContent = formatted;
    }

    displayChat(data) {
        const chatContainer = document.getElementById('chatContainer');
        
        // Remove empty message if exists
        const emptyMsg = chatContainer.querySelector('.chat-empty');
        if (emptyMsg) emptyMsg.remove();
        
        // Create chat message
        const messageDiv = document.createElement('div');
        messageDiv.className = 'chat-message';
        messageDiv.innerHTML = `
            <div class="username">${data.username}</div>
            <div class="message">${data.message}</div>
        `;
        
        chatContainer.appendChild(messageDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;
        
        // Auto response
        if (document.getElementById('autoGreeting').checked && data.isNewUser) {
            this.autoReply(`Halo @${data.username}! Selamat datang di live saya 👋`);
        }
    }

    displayGift(data) {
        const giftsList = document.getElementById('giftsList');
        
        // Remove empty message if exists
        const emptyMsg = giftsList.querySelector('.gift-empty');
        if (emptyMsg) emptyMsg.remove();
        
        // Create gift item
        const giftDiv = document.createElement('div');
        giftDiv.className = 'gift-item';
        giftDiv.innerHTML = `
            <div class="icon">🎁</div>
            <div class="info">
                <div class="username">${data.username}</div>
                <div class="gift-name">${data.gift_name} x${data.count}</div>
            </div>
        `;
        
        giftsList.insertBefore(giftDiv, giftsList.firstChild);
        
        // Auto thank
        if (document.getElementById('autoThankGift').checked) {
            this.autoReply(`Terima kasih @${data.username} untuk ${data.gift_name}! 💖`);
        }
    }

    sendChat() {
        const chatInput = document.getElementById('chatInput');
        const message = chatInput.value.trim();
        
        if (!message) return;
        
        // Send to TikTok
        this.socket.emit('send_chat', { message });
        
        chatInput.value = '';
        this.showNotification('Chat terkirim', 'success');
    }

    autoReply(message) {
        setTimeout(() => {
            this.chatQueue.push({
                id: Date.now(),
                text: message
            });
            this.updateQueueDisplay();
            this.processQueue();
        }, 1000);
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 1rem 1.5rem;
            background: ${type === 'success' ? '#00d856' : type === 'error' ? '#fe2c55' : '#25f4ee'};
            color: white;
            border-radius: 8px;
            z-index: 10000;
            animation: slideIn 0.3s ease;
        `;
        
        document.body.appendChild(notification);
        
        // Remove after 3 seconds
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }
}

// Initialize app
const app = new TikTokLiveAI();

