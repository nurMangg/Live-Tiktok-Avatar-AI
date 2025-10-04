const express = require('express');
const http = require('http');
const socketIo = require('socket.io');
const cors = require('cors');
const axios = require('axios');
require('dotenv').config();

const app = express();
const server = http.createServer(app);
const io = socketIo(server, {
    cors: {
        origin: "*",
        methods: ["GET", "POST"]
    }
});

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static(__dirname));

// Configuration
const PORT = process.env.PORT || 3000;
const PYTHON_PORT = process.env.PYTHON_PORT || 5000;

// Store active streams
const activeStreams = new Map();

// Routes
app.get('/', (req, res) => {
    res.sendFile(__dirname + '/index.html');
});

// TikTok OAuth Callback
app.get('/auth/callback', async (req, res) => {
    const { code } = req.query;
    
    try {
        // Exchange code for access token
        const tokenResponse = await axios.post('https://open-api.tiktok.com/oauth/access_token/', {
            client_key: process.env.TIKTOK_CLIENT_KEY,
            client_secret: process.env.TIKTOK_CLIENT_SECRET,
            code: code,
            grant_type: 'authorization_code',
            redirect_uri: process.env.TIKTOK_REDIRECT_URI
        });
        
        const accessToken = tokenResponse.data.data.access_token;
        
        // Get user info
        const userResponse = await axios.get('https://open-api.tiktok.com/user/info/', {
            headers: {
                'Authorization': `Bearer ${accessToken}`
            }
        });
        
        const userData = userResponse.data.data.user;
        
        // Send response to parent window
        res.send(`
            <script>
                window.opener.postMessage({
                    type: 'tiktok-auth',
                    token: '${accessToken}',
                    user: ${JSON.stringify(userData)}
                }, '*');
                window.close();
            </script>
        `);
    } catch (error) {
        console.error('TikTok auth error:', error);
        res.status(500).send('Authentication failed');
    }
});

// Socket.IO Events
io.on('connection', (socket) => {
    console.log('Client connected:', socket.id);
    
    // Avatar change
    socket.on('avatar_change', (data) => {
        console.log('Avatar changed:', data.avatar);
        // Send to Python backend for AI processing
        notifyPythonBackend('avatar_change', data);
    });
    
    // Product added
    socket.on('product_added', (data) => {
        console.log('Product added:', data.name);
        // In production, save to database
    });
    
    // Start streaming
    socket.on('start_stream', async (settings) => {
        console.log('Stream starting with settings:', settings);
        
        activeStreams.set(socket.id, {
            settings,
            startTime: Date.now(),
            viewers: 0,
            likes: 0,
            comments: 0
        });
        
        // Initialize stream with Python backend
        try {
            await axios.post(`http://localhost:${PYTHON_PORT}/api/stream/start`, {
                socketId: socket.id,
                settings
            });
            
            socket.emit('stream_started', { success: true });
            
            // Simulate live stats updates
            simulateLiveStats(socket);
        } catch (error) {
            console.error('Error starting stream:', error);
            socket.emit('stream_error', { message: 'Failed to start stream' });
        }
    });
    
    // Stop streaming
    socket.on('stop_stream', async () => {
        console.log('Stream stopping');
        
        try {
            await axios.post(`http://localhost:${PYTHON_PORT}/api/stream/stop`, {
                socketId: socket.id
            });
            
            activeStreams.delete(socket.id);
            socket.emit('stream_stopped', { success: true });
        } catch (error) {
            console.error('Error stopping stream:', error);
        }
    });
    
    // Toggle avatar
    socket.on('toggle_avatar', (data) => {
        console.log('Avatar toggle:', data.enabled);
        notifyPythonBackend('toggle_avatar', data);
    });
    
    // Speak text with AI avatar
    socket.on('speak', async (data) => {
        console.log('AI speaking:', data.text);
        
        try {
            await axios.post(`http://localhost:${PYTHON_PORT}/api/avatar/speak`, data);
        } catch (error) {
            console.error('Error making avatar speak:', error);
        }
    });
    
    // Send chat message
    socket.on('send_chat', (data) => {
        console.log('Sending chat:', data.message);
        // In production, this would send to TikTok API
        socket.emit('chat_sent', { success: true });
    });
    
    socket.on('disconnect', () => {
        console.log('Client disconnected:', socket.id);
        activeStreams.delete(socket.id);
    });
});

// Helper function to notify Python backend
async function notifyPythonBackend(event, data) {
    try {
        await axios.post(`http://localhost:${PYTHON_PORT}/api/event`, {
            event,
            data
        });
    } catch (error) {
        console.error('Error notifying Python backend:', error.message);
    }
}

// Simulate live stream stats
function simulateLiveStats(socket) {
    const streamData = activeStreams.get(socket.id);
    if (!streamData) return;
    
    const interval = setInterval(() => {
        if (!activeStreams.has(socket.id)) {
            clearInterval(interval);
            return;
        }
        
        // Simulate random stats
        streamData.viewers += Math.floor(Math.random() * 5);
        streamData.likes += Math.floor(Math.random() * 10);
        streamData.comments += Math.floor(Math.random() * 3);
        
        socket.emit('viewer_count', streamData.viewers);
        socket.emit('like', streamData.likes);
        socket.emit('comment_count', streamData.comments);
        
        // Simulate random chat messages
        if (Math.random() > 0.7) {
            const usernames = ['User123', 'TikTokFan', 'Viewer456', 'LiveWatcher', 'FanAccount'];
            const messages = [
                'Keren banget!',
                'Halo from Jakarta!',
                'Love your content!',
                'Amazing stream!',
                'Salam dari Surabaya'
            ];
            
            socket.emit('chat', {
                username: usernames[Math.floor(Math.random() * usernames.length)],
                message: messages[Math.floor(Math.random() * messages.length)],
                isNewUser: Math.random() > 0.8
            });
        }
        
        // Simulate random gifts
        if (Math.random() > 0.9) {
            const gifts = [
                { name: 'Rose', icon: '🌹' },
                { name: 'Heart', icon: '❤️' },
                { name: 'Diamond', icon: '💎' },
                { name: 'Crown', icon: '👑' }
            ];
            
            const gift = gifts[Math.floor(Math.random() * gifts.length)];
            
            socket.emit('gift', {
                username: 'Supporter' + Math.floor(Math.random() * 1000),
                gift_name: gift.name,
                count: Math.floor(Math.random() * 5) + 1
            });
        }
        
        // Simulate random orders (for demo)
        if (Math.random() > 0.95) {
            const products = [
                'Serum Wajah Glowing',
                'Lipstick Matte',
                'Cream Pemutih',
                'Masker Wajah',
                'Parfum Premium'
            ];
            
            const amounts = [99000, 149000, 199000, 249000, 299000];
            
            socket.emit('new_order', {
                customer: 'Buyer' + Math.floor(Math.random() * 1000),
                product: products[Math.floor(Math.random() * products.length)],
                quantity: Math.floor(Math.random() * 3) + 1,
                amount: amounts[Math.floor(Math.random() * amounts.length)]
            });
        }
    }, 5000);
}

// Start server
server.listen(PORT, () => {
    console.log(`Server running on http://localhost:${PORT}`);
    console.log('TikTok Live AI Avatar application started');
});

