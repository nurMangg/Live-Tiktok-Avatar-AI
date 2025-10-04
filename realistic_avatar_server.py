#!/usr/bin/env python3
"""
Realistic Human Avatar Server - Using Real Photos
Menggunakan foto orang asli untuk avatar yang realistis
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os
import json
import time
import requests
from io import BytesIO
import base64
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

class RealisticAvatar:
    """Realistic Human Avatar using real photos"""
    
    def __init__(self, avatar_type='female'):
        self.avatar_type = avatar_type
        self.current_frame = None
        self.is_speaking = False
        self.face_image = None
        self.load_realistic_avatar()
        
    def load_realistic_avatar(self):
        """Load realistic human avatar from real photos"""
        try:
            # Download realistic human photos from Pravatar (free service)
            if self.avatar_type == 'female':
                # Professional female avatar
                avatar_url = "https://i.pravatar.cc/400?img=5"  # Professional woman
            elif self.avatar_type == 'male':
                # Professional male avatar  
                avatar_url = "https://i.pravatar.cc/400?img=12"  # Professional man
            else:
                # Default professional woman
                avatar_url = "https://i.pravatar.cc/400?img=1"
            
            # Download image
            response = requests.get(avatar_url, timeout=10)
            if response.status_code == 200:
                # Convert to OpenCV format
                img_array = np.array(bytearray(response.content), dtype=np.uint8)
                self.face_image = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                
                # Resize to standard size
                self.face_image = cv2.resize(self.face_image, (400, 400))
                print(f"✅ Loaded realistic {self.avatar_type} avatar from {avatar_url}")
            else:
                self.create_fallback_avatar()
                
        except Exception as e:
            print(f"❌ Error loading realistic avatar: {e}")
            self.create_fallback_avatar()
    
    def create_fallback_avatar(self):
        """Create fallback realistic avatar if download fails"""
        print("Creating fallback realistic avatar...")
        
        # Create realistic face using OpenCV
        img = np.zeros((400, 400, 3), dtype=np.uint8)
        
        # Skin tone
        skin_color = (220, 190, 170) if self.avatar_type == 'female' else (200, 170, 150)
        
        # Face oval
        cv2.ellipse(img, (200, 200), (180, 220), 0, 0, 360, skin_color, -1)
        
        # Hair
        hair_color = (40, 30, 20) if self.avatar_type == 'female' else (30, 20, 10)
        cv2.ellipse(img, (200, 150), (200, 180), 0, 180, 360, hair_color, -1)
        
        # Eyes
        eye_color = (100, 60, 30)  # Brown eyes
        cv2.ellipse(img, (160, 180), (25, 15), 0, 0, 360, (255, 255, 255), -1)  # Left eye white
        cv2.ellipse(img, (240, 180), (25, 15), 0, 0, 360, (255, 255, 255), -1)  # Right eye white
        cv2.circle(img, (160, 180), 12, eye_color, -1)  # Left iris
        cv2.circle(img, (240, 180), 12, eye_color, -1)  # Right iris
        cv2.circle(img, (160, 180), 6, (0, 0, 0), -1)   # Left pupil
        cv2.circle(img, (240, 180), 6, (0, 0, 0), -1)   # Right pupil
        
        # Nose
        cv2.ellipse(img, (200, 220), (15, 20), 0, 0, 180, (180, 150, 130), -1)
        
        # Mouth
        cv2.ellipse(img, (200, 260), (30, 15), 0, 0, 180, (180, 100, 100), -1)
        
        # Blush
        cv2.ellipse(img, (120, 240), (20, 15), 0, 0, 360, (240, 180, 180), -1)
        cv2.ellipse(img, (280, 240), (20, 15), 0, 0, 360, (240, 180, 180), -1)
        
        self.face_image = img
        print("✅ Created fallback realistic avatar")
    
    def create_portrait_frame(self, gesture_intensity=50):
        """Create portrait frame with realistic human avatar"""
        # Portrait dimensions for TikTok (9:16)
        frame = np.zeros((1920, 1080, 3), dtype=np.uint8)
        
        # Animated gradient background
        t = time.time()
        for i in range(1920):
            color_r = int(40 + abs(np.sin((i + t * 20) / 200)) * 60)
            color_g = int(50 + abs(np.sin((i + t * 20 + 120) / 200)) * 70)
            color_b = int(80 + abs(np.sin((i + t * 20 + 240) / 200)) * 80)
            frame[i, :] = [color_b, color_g, color_r]
        
        if self.face_image is not None:
            # Resize face to fit portrait
            face_resized = cv2.resize(self.face_image, (600, 600))
            
            # Apply gesture animation
            face_animated = self.apply_gesture_to_face(face_resized, gesture_intensity)
            
            # Position face in center of portrait
            y_offset = 300
            x_offset = 240
            
            # Blend face onto background
            h, w = face_animated.shape[:2]
            frame[y_offset:y_offset+h, x_offset:x_offset+w] = face_animated
            
            # Add professional clothing/body
            self.add_professional_body(frame, x_offset, y_offset + h)
        
        # Add UI overlays
        self.add_ui_overlays(frame, gesture_intensity)
        
        return frame
    
    def apply_gesture_to_face(self, face_img, intensity):
        """Apply realistic gestures to face"""
        t = time.time()
        intensity_factor = intensity / 100.0
        
        # Slight head tilt
        if intensity > 20:
            angle = np.sin(t * 1.5) * (intensity_factor * 2)
            center = (face_img.shape[1]//2, face_img.shape[0]//2)
            M = cv2.getRotationMatrix2D(center, angle, 1.0)
            face_img = cv2.warpAffine(face_img, M, (face_img.shape[1], face_img.shape[0]))
        
        # Speaking animation
        if self.is_speaking and intensity > 30:
            mouth_open = abs(np.sin(t * 8)) * intensity_factor
            if mouth_open > 0.5:
                # Draw open mouth
                mouth_y = face_img.shape[0] - 80
                cv2.ellipse(face_img, (face_img.shape[1]//2, mouth_y), 
                          (int(30 + mouth_open * 20), int(15 + mouth_open * 10)), 
                          0, 0, 180, (100, 50, 50), -1)
        
        # Breathing effect
        if intensity > 10:
            scale = 1.0 + np.sin(t * 0.8) * 0.01 * intensity_factor
            h, w = face_img.shape[:2]
            M = cv2.getRotationMatrix2D((w//2, h//2), 0, scale)
            face_img = cv2.warpAffine(face_img, M, (w, h))
        
        # Blinking
        if int(t * 3) % 10 == 0 and (t % 1) < 0.15:
            eye_y = face_img.shape[0] - 220
            cv2.line(face_img, (face_img.shape[1]//2 - 50, eye_y), 
                    (face_img.shape[1]//2 - 20, eye_y), (220, 190, 170), 3)
            cv2.line(face_img, (face_img.shape[1]//2 + 20, eye_y), 
                    (face_img.shape[1]//2 + 50, eye_y), (220, 190, 170), 3)
        
        return face_img
    
    def add_professional_body(self, frame, x_offset, y_start):
        """Add professional clothing/body to avatar"""
        # Neck
        neck_color = (200, 170, 150)
        cv2.rectangle(frame, (x_offset + 200, y_start), (x_offset + 400, y_start + 100), neck_color, -1)
        
        # Professional clothing
        clothing_color = (30, 30, 50)  # Dark professional
        cv2.rectangle(frame, (x_offset + 100, y_start + 100), (x_offset + 500, y_start + 400), clothing_color, -1)
        
        # Shoulders
        cv2.ellipse(frame, (x_offset + 300, y_start + 100), (200, 80), 0, 0, 180, clothing_color, -1)
    
    def add_ui_overlays(self, frame, gesture_intensity):
        """Add UI overlays to frame"""
        # Top status bar
        cv2.rectangle(frame, (0, 0), (1080, 80), (0, 0, 0), -1)
        cv2.rectangle(frame, (0, 0), (1080, 80), (37, 244, 238), 2)
        
        # Status text
        status_text = f"REALISTIC AVATAR | {self.avatar_type.upper()} | Gesture: {gesture_intensity}%"
        cv2.putText(frame, status_text, (30, 50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (37, 244, 238), 2)
        
        # Speaking indicator
        if self.is_speaking:
            cv2.circle(frame, (1020, 40), 20, (0, 255, 0), -1)
            cv2.putText(frame, "SPEAKING", (900, 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        else:
            cv2.circle(frame, (1020, 40), 20, (100, 100, 100), -1)
        
        # Bottom info
        cv2.putText(frame, "TikTok Live Shopping - Real Human Avatar", (30, 1890), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    def speak(self, text, voice_type='female-1', speed=1.0, pitch=0):
        """Make avatar speak"""
        self.is_speaking = True
        
        duration = len(text) / 10 * speed
        
        print(f"🗣️ Realistic Avatar speaking: {text}")
        print(f"   Voice: {voice_type}, Speed: {speed}x, Pitch: {pitch}")
        
        # Auto-stop speaking
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
        """Process and return current frame"""
        return self.create_portrait_frame(gesture_intensity)


class StreamManager:
    """Manage live streaming sessions"""
    
    def __init__(self):
        self.streams = {}
        self.global_avatar = RealisticAvatar('female')
    
    def create_stream(self, socket_id, settings):
        """Create a new stream session"""
        avatar_type = settings.get('avatar', 'female')
        avatar = RealisticAvatar(avatar_type)
        
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
        self.global_avatar = RealisticAvatar(avatar_type)
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
        'version': '2.0.0',
        'avatar_type': 'realistic_human'
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
            'message': 'Realistic avatar stream started successfully',
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
    """Make realistic avatar speak text"""
    data = request.json
    text = data.get('text', '')
    voice = data.get('voice', 'female-1')
    speed = float(data.get('speed', 1.0))
    pitch = int(data.get('pitch', 0))
    avatar_type = data.get('avatar', 'female')
    
    try:
        # Find active stream with this avatar
        avatar = None
        for stream_data in stream_manager.streams.values():
            if stream_data['avatar'].avatar_type == avatar_type:
                avatar = stream_data['avatar']
                break
        
        if not avatar:
            # Create temporary avatar
            avatar = RealisticAvatar(avatar_type)
        
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


@app.route('/api/avatar/change', methods=['POST'])
def change_avatar():
    """Change avatar type to realistic human"""
    data = request.json
    avatar_type = data.get('avatar', 'female')
    
    try:
        stream_manager.change_avatar(avatar_type)
        
        return jsonify({
            'success': True,
            'message': f'Changed to realistic {avatar_type} avatar'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/frame/<socket_id>', methods=['GET'])
def get_frame(socket_id):
    """Get current realistic avatar frame"""
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
    _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 90])
    
    return buffer.tobytes(), 200, {'Content-Type': 'image/jpeg'}


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
        avatar_type = event_data.get('avatar', 'female')
        stream_manager.change_avatar(avatar_type)
    elif event == 'toggle_avatar':
        # Handle avatar toggle
        pass
    
    return jsonify({'success': True})


# WebSocket events
@socketio.on('connect')
def handle_connect():
    print('Realistic Avatar client connected')


@socketio.on('disconnect')
def handle_disconnect():
    print('Realistic Avatar client disconnected')


# Main
if __name__ == '__main__':
    print(f"🚀 Starting REALISTIC HUMAN AVATAR Server on port {PORT}")
    print(f"👤 Using REAL PHOTOS for avatars")
    print(f"📱 Portrait Mode (9:16): 1080x1920")
    print(f"🎭 Avatar Types: Female, Male (Realistic)")
    print(f"🔗 Server ready at http://localhost:{PORT}")
    
    socketio.run(app, host='0.0.0.0', port=PORT, debug=False, allow_unsafe_werkzeug=True)
