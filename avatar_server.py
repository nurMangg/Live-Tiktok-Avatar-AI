#!/usr/bin/env python3
"""
TikTok Live AI Avatar Backend Server
Handles AI avatar processing, speech synthesis, and video generation
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO
import cv2
import numpy as np
from PIL import Image
import os
import json
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Configuration
PORT = int(os.getenv('PYTHON_PORT', 5000))
AVATAR_DIR = 'avatars'
TEMP_DIR = 'temp'

# Ensure directories exist
os.makedirs(AVATAR_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

# Store active sessions
active_sessions = {}

class AIAvatar:
    """AI Avatar processor class"""
    
    def __init__(self, avatar_type='default'):
        self.avatar_type = avatar_type
        self.current_frame = None
        self.is_speaking = False
        
    def load_avatar(self, avatar_path=None):
        """Load avatar model or image"""
        if avatar_path and os.path.exists(avatar_path):
            self.avatar_image = cv2.imread(avatar_path)
        else:
            # Create default avatar (placeholder)
            self.avatar_image = self.create_default_avatar()
        
        return True
    
    def create_default_avatar(self):
        """Create a default avatar with better design - Portrait mode for TikTok"""
        # TikTok portrait mode: 1080x1920 (9:16 ratio)
        img = np.zeros((1920, 1080, 3), dtype=np.uint8)
        
        # Create professional gradient background (portrait)
        time_factor = int(time.time() * 20) % 360
        for i in range(1920):
            # Soft gradient from dark to light
            color_r = int(40 + abs(np.sin((i + time_factor) / 200)) * 60)
            color_g = int(50 + abs(np.sin((i + time_factor + 120) / 200)) * 70)
            color_b = int(80 + abs(np.sin((i + time_factor + 240) / 200)) * 80)
            img[i, :] = [color_b, color_g, color_r]
        
        # Create realistic human avatar (portrait style)
        center_x = 540  # Center for portrait
        center_y = 960  # Center vertically
        
        # === BODY & CLOTHING ===
        # Shoulders and upper body
        body_points = np.array([
            [center_x - 280, 1920],  # Bottom left
            [center_x + 280, 1920],  # Bottom right
            [center_x + 200, center_y + 400],  # Right shoulder
            [center_x + 120, center_y + 200],  # Right neck
            [center_x - 120, center_y + 200],  # Left neck
            [center_x - 200, center_y + 400],  # Left shoulder
        ])
        # Dark clothing
        cv2.fillPoly(img, [body_points], (30, 30, 50))
        
        # Neck
        neck_points = np.array([
            [center_x - 80, center_y + 200],
            [center_x + 80, center_y + 200],
            [center_x + 90, center_y + 320],
            [center_x - 90, center_y + 320]
        ])
        cv2.fillPoly(img, [neck_points], (200, 170, 150))
        
        # === HEAD & FACE ===
        # Head shape (oval for realistic face)
        face_color = (220, 190, 170)  # Realistic skin tone
        
        # Main face oval
        cv2.ellipse(img, (center_x, center_y + 60), (180, 240), 0, 0, 360, face_color, -1)
        
        # Forehead highlight
        cv2.ellipse(img, (center_x, center_y - 50), (140, 100), 0, 0, 360, (230, 200, 180), -1)
        
        # === HAIR ===
        # Female hairstyle
        if self.avatar_type in ['default', 'female']:
            # Long hair
            cv2.ellipse(img, (center_x, center_y - 100), (200, 280), 0, 0, 360, (40, 30, 20), -1)
            # Hair sides
            cv2.ellipse(img, (center_x - 140, center_y + 80), (100, 200), 20, 0, 360, (50, 35, 25), -1)
            cv2.ellipse(img, (center_x + 140, center_y + 80), (100, 200), -20, 0, 360, (50, 35, 25), -1)
            # Hair highlights
            cv2.ellipse(img, (center_x - 40, center_y - 120), (80, 120), 10, 0, 180, (70, 50, 35), -1)
        else:
            # Male short hair
            cv2.ellipse(img, (center_x, center_y - 80), (190, 200), 0, 180, 360, (35, 25, 15), -1)
        
        # === EYES ===
        eye_y = center_y + 20
        eye_left = (center_x - 70, eye_y)
        eye_right = (center_x + 70, eye_y)
        
        # Eye sockets (shadow)
        cv2.ellipse(img, eye_left, (45, 30), 0, 0, 360, (190, 160, 140), -1)
        cv2.ellipse(img, eye_right, (45, 30), 0, 0, 360, (190, 160, 140), -1)
        
        # Eye whites
        cv2.ellipse(img, eye_left, (40, 25), 0, 0, 360, (255, 255, 250), -1)
        cv2.ellipse(img, eye_right, (40, 25), 0, 0, 360, (255, 255, 250), -1)
        
        # Iris (brown/hazel)
        for r in range(22, 0, -2):
            intensity_r = int(80 + (22-r) * 6)
            intensity_g = int(50 + (22-r) * 4)
            intensity_b = int(30 + (22-r) * 2)
            cv2.circle(img, eye_left, r, (intensity_b, intensity_g, intensity_r), -1)
            cv2.circle(img, eye_right, r, (intensity_b, intensity_g, intensity_r), -1)
        
        # Pupils
        cv2.circle(img, eye_left, 10, (10, 10, 10), -1)
        cv2.circle(img, eye_right, 10, (10, 10, 10), -1)
        
        # Eye highlights (realistic reflection)
        cv2.circle(img, (eye_left[0] - 5, eye_left[1] - 5), 6, (255, 255, 255), -1)
        cv2.circle(img, (eye_right[0] - 5, eye_right[1] - 5), 6, (255, 255, 255), -1)
        cv2.circle(img, (eye_left[0] + 8, eye_left[1] + 8), 3, (200, 200, 200), -1)
        cv2.circle(img, (eye_right[0] + 8, eye_right[1] + 8), 3, (200, 200, 200), -1)
        
        # Upper eyelids
        cv2.ellipse(img, eye_left, (42, 28), 0, 200, 340, (180, 150, 130), 3)
        cv2.ellipse(img, eye_right, (42, 28), 0, 200, 340, (180, 150, 130), 3)
        
        # === EYEBROWS ===
        cv2.ellipse(img, (center_x - 70, eye_y - 45), (50, 18), 165, 0, 180, (60, 40, 25), 5)
        cv2.ellipse(img, (center_x + 70, eye_y - 45), (50, 18), 15, 0, 180, (60, 40, 25), 5)
        
        # === NOSE ===
        nose_y = center_y + 80
        # Nose bridge shadow
        cv2.line(img, (center_x - 5, eye_y + 20), (center_x - 8, nose_y), (190, 160, 140), 2)
        # Nose tip
        cv2.ellipse(img, (center_x, nose_y), (25, 20), 0, 0, 180, (210, 180, 160), -1)
        # Nostrils
        cv2.ellipse(img, (center_x - 15, nose_y + 10), (8, 12), 30, 0, 180, (180, 150, 130), -1)
        cv2.ellipse(img, (center_x + 15, nose_y + 10), (8, 12), -30, 0, 180, (180, 150, 130), -1)
        
        # === MOUTH ===
        mouth_y = center_y + 150
        # Upper lip
        cv2.ellipse(img, (center_x, mouth_y - 10), (50, 15), 0, 0, 180, (180, 100, 100), -1)
        # Lower lip
        cv2.ellipse(img, (center_x, mouth_y + 5), (45, 20), 0, 180, 360, (200, 120, 120), -1)
        # Lip shine
        cv2.ellipse(img, (center_x, mouth_y + 8), (35, 10), 0, 180, 360, (220, 140, 140), -1)
        # Smile line
        cv2.ellipse(img, (center_x, mouth_y), (55, 30), 0, 15, 165, (160, 80, 80), 2)
        # Teeth (subtle)
        cv2.ellipse(img, (center_x, mouth_y - 5), (40, 10), 0, 0, 180, (245, 245, 240), -1)
        
        # === FACIAL FEATURES ===
        # Cheekbones highlight
        cv2.ellipse(img, (center_x - 100, center_y + 70), (50, 35), -20, 0, 360, (235, 205, 185), -1)
        cv2.ellipse(img, (center_x + 100, center_y + 70), (50, 35), 20, 0, 360, (235, 205, 185), -1)
        
        # Blush (natural)
        cv2.ellipse(img, (center_x - 110, center_y + 80), (45, 30), 0, 0, 360, (240, 170, 170), -1)
        cv2.ellipse(img, (center_x + 110, center_y + 80), (45, 30), 0, 0, 360, (240, 170, 170), -1)
        
        # Chin shadow
        cv2.ellipse(img, (center_x, center_y + 220), (70, 40), 0, 0, 180, (200, 170, 150), -1)
        
        # Apply subtle blur for smooth skin
        img = cv2.GaussianBlur(img, (5, 5), 0)
        
        # === TEXT LABELS ===
        avatar_name = "Female Avatar" if self.avatar_type in ['default', 'female'] else "Male Avatar"
        cv2.putText(img, avatar_name, (center_x - 150, 1800), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3)
        cv2.putText(img, "Live Shopping AI", (center_x - 140, 1850), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (200, 200, 200), 2)
        
        return img
    
    def apply_gesture(self, intensity=50):
        """Apply gesture animation to avatar - Portrait mode"""
        if self.avatar_image is None:
            self.avatar_image = self.create_default_avatar()
        
        # Recreate avatar with animation (for dynamic background)
        frame = self.create_default_avatar()
        
        # Apply various animations based on intensity
        t = time.time()
        intensity_factor = intensity / 100.0
        
        # Portrait center
        center_x = 540
        center_y = 960
        
        # Slight head tilt/rotation
        if intensity > 20:
            angle = np.sin(t * 1.5) * (intensity_factor * 2)
            M = cv2.getRotationMatrix2D((center_x, center_y), angle, 1.0)
            frame = cv2.warpAffine(frame, M, (frame.shape[1], frame.shape[0]))
        
        # Speaking animation - mouth movement
        if self.is_speaking and intensity > 30:
            mouth_open = abs(np.sin(t * 8)) * intensity_factor
            if mouth_open > 0.5:
                # Draw open mouth when speaking
                mouth_y = center_y + 150
                cv2.ellipse(frame, (center_x, mouth_y + 5), 
                          (50, int(20 + mouth_open * 20)), 
                          0, 0, 180, (100, 50, 50), -1)
        
        # Breathing effect - subtle scale
        if intensity > 10:
            scale = 1.0 + np.sin(t * 0.8) * 0.008 * intensity_factor
            h, w = frame.shape[:2]
            M = cv2.getRotationMatrix2D((w/2, h/2), 0, scale)
            frame = cv2.warpAffine(frame, M, (w, h))
        
        # Blinking animation (occasional)
        if int(t * 3) % 10 == 0 and (t % 1) < 0.15:
            # Draw closed eyes
            eye_y = center_y + 20
            cv2.line(frame, (center_x - 110, eye_y), (center_x - 30, eye_y), (180, 150, 130), 4)
            cv2.line(frame, (center_x + 30, eye_y), (center_x + 110, eye_y), (180, 150, 130), 4)
        
        # === UI OVERLAYS ===
        # Top status bar
        cv2.rectangle(frame, (0, 0), (1080, 80), (0, 0, 0), -1)
        cv2.rectangle(frame, (0, 0), (1080, 80), (37, 244, 238), 2)
        
        # FPS and status
        fps_text = f"AI AVATAR | Gesture: {intensity}%"
        cv2.putText(frame, fps_text, (30, 50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (37, 244, 238), 2)
        
        # Speaking indicator
        if self.is_speaking:
            cv2.circle(frame, (1020, 40), 20, (0, 255, 0), -1)
            cv2.putText(frame, "LIVE", (950, 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        else:
            cv2.circle(frame, (1020, 40), 20, (100, 100, 100), -1)
        
        # Bottom watermark
        cv2.putText(frame, "TikTok Live Shopping", (30, 1890), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        return frame
    
    def speak(self, text, voice_type='female-1', speed=1.0, pitch=0):
        """Generate speech and lip-sync animation"""
        self.is_speaking = True
        
        # In production, integrate with TTS (Text-to-Speech) API
        # For now, simulate speaking duration
        duration = len(text) / 10 * speed  # rough estimate
        
        print(f"🗣️ Avatar speaking: {text}")
        print(f"   Voice: {voice_type}, Speed: {speed}x, Pitch: {pitch}")
        
        # TODO: Integrate with real TTS service like:
        # - Google Cloud Text-to-Speech
        # - Amazon Polly
        # - Microsoft Azure Speech
        # - ElevenLabs (for realistic voices)
        # - Coqui TTS (Open source)
        
        # Auto-stop speaking after duration
        import threading
        def stop_speaking():
            time.sleep(duration)
            self.is_speaking = False
        
        threading.Thread(target=stop_speaking, daemon=True).start()
        
        return {
            'success': True,
            'duration': duration,
            'text': text,
            'voice': voice_type
        }
    
    def process_frame(self, gesture_intensity=50):
        """Process and return current avatar frame"""
        return self.apply_gesture(gesture_intensity)


class StreamManager:
    """Manage live streaming sessions"""
    
    def __init__(self):
        self.streams = {}
        self.global_avatar = AIAvatar('default')
        self.global_avatar.load_avatar()
    
    def create_stream(self, socket_id, settings):
        """Create a new stream session"""
        avatar_type = settings.get('avatar', 'default')
        avatar = AIAvatar(avatar_type)
        avatar.load_avatar()
        
        self.streams[socket_id] = {
            'avatar': avatar,
            'settings': settings,
            'start_time': time.time(),
            'frame_count': 0
        }
        
        return True
    
    def get_stream(self, socket_id):
        """Get stream session"""
        return self.streams.get(socket_id)
    
    def stop_stream(self, socket_id):
        """Stop and cleanup stream session"""
        if socket_id in self.streams:
            del self.streams[socket_id]
            return True
        return False
    
    def get_avatar(self):
        """Get global avatar for preview"""
        return self.global_avatar
    
    def change_avatar(self, avatar_type):
        """Change global avatar"""
        self.global_avatar = AIAvatar(avatar_type)
        self.global_avatar.load_avatar()
        return True


# Initialize stream manager
stream_manager = StreamManager()


# API Routes

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'active_streams': len(stream_manager.streams),
        'version': '1.0.0'
    })


@app.route('/api/stream/start', methods=['POST'])
def start_stream():
    """Start a new stream session"""
    data = request.json
    socket_id = data.get('socketId')
    settings = data.get('settings', {})
    
    try:
        stream_manager.create_stream(socket_id, settings)
        
        return jsonify({
            'success': True,
            'message': 'Stream started successfully',
            'socket_id': socket_id
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/stream/stop', methods=['POST'])
def stop_stream():
    """Stop a stream session"""
    data = request.json
    socket_id = data.get('socketId')
    
    try:
        stream_manager.stop_stream(socket_id)
        
        return jsonify({
            'success': True,
            'message': 'Stream stopped successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/avatar/speak', methods=['POST'])
def avatar_speak():
    """Make avatar speak text"""
    data = request.json
    text = data.get('text', '')
    voice = data.get('voice', 'female-1')
    speed = float(data.get('speed', 1.0))
    pitch = int(data.get('pitch', 0))
    avatar_type = data.get('avatar', 'default')
    
    try:
        # Find active stream with this avatar
        avatar = None
        for stream_data in stream_manager.streams.values():
            if stream_data['avatar'].avatar_type == avatar_type:
                avatar = stream_data['avatar']
                break
        
        if not avatar:
            # Create temporary avatar
            avatar = AIAvatar(avatar_type)
            avatar.load_avatar()
        
        result = avatar.speak(text, voice, speed, pitch)
        
        return jsonify({
            'success': True,
            'result': result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/avatar/upload', methods=['POST'])
def upload_avatar():
    """Upload custom avatar"""
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'}), 400
    
    try:
        # Save uploaded file
        filename = f"custom_{int(time.time())}_{file.filename}"
        filepath = os.path.join(AVATAR_DIR, filename)
        file.save(filepath)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'path': filepath
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/avatar/change', methods=['POST'])
def change_avatar():
    """Change avatar type"""
    data = request.json
    avatar_type = data.get('avatar', 'default')
    
    try:
        stream_manager.change_avatar(avatar_type)
        
        return jsonify({
            'success': True,
            'message': f'Avatar changed to {avatar_type}'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/event', methods=['POST'])
def handle_event():
    """Handle events from Node.js backend"""
    data = request.json
    event = data.get('event')
    event_data = data.get('data', {})
    
    print(f"Received event: {event}")
    print(f"Event data: {event_data}")
    
    # Process event based on type
    if event == 'avatar_change':
        avatar_type = event_data.get('avatar', 'default')
        stream_manager.change_avatar(avatar_type)
    elif event == 'toggle_avatar':
        # Handle avatar toggle
        pass
    
    return jsonify({'success': True})


@app.route('/api/frame/<socket_id>', methods=['GET'])
def get_frame(socket_id):
    """Get current frame for a stream"""
    # For preview/non-stream, use global avatar
    if socket_id == 'avatar_stream':
        avatar = stream_manager.get_avatar()
    else:
        stream = stream_manager.get_stream(socket_id)
        if not stream:
            return jsonify({'error': 'Stream not found'}), 404
        avatar = stream['avatar']
    
    gesture_intensity = int(request.args.get('gesture', 50))
    
    frame = avatar.process_frame(gesture_intensity)
    
    if frame is None:
        return jsonify({'error': 'Failed to generate frame'}), 500
    
    # Encode frame to JPEG
    _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
    
    return buffer.tobytes(), 200, {'Content-Type': 'image/jpeg'}


# WebSocket events
@socketio.on('connect')
def handle_connect():
    print('Python backend client connected')


@socketio.on('disconnect')
def handle_disconnect():
    print('Python backend client disconnected')


# Main
if __name__ == '__main__':
    print(f"Starting AI Avatar Backend Server on port {PORT}")
    print(f"Avatar directory: {AVATAR_DIR}")
    print(f"Temp directory: {TEMP_DIR}")
    print(f"🤖 Realistic Human Avatar Mode: ACTIVE")
    print(f"📱 Portrait Mode (9:16): 1080x1920")
    print(f"🚀 Server ready at http://localhost:{PORT}")
    
    socketio.run(app, host='0.0.0.0', port=PORT, debug=False, allow_unsafe_werkzeug=True)

