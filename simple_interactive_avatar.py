#!/usr/bin/env python3
"""
Simple Interactive Avatar Server
Avatar yang bisa berinteraksi dengan mimik mulut dan gerak-gerik real-time
Tanpa dependensi rumit, hanya OpenCV dan numpy
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
import threading
import queue
import math

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

class SimpleInteractiveAvatar:
    """Simple Interactive Avatar dengan animasi real-time"""
    
    def __init__(self, avatar_type='female'):
        self.avatar_type = avatar_type
        self.current_frame = None
        self.is_speaking = False
        self.face_image = None
        self.animation_state = {
            'mouth_open': 0.0,
            'eye_blink': 0.0,
            'head_tilt': 0.0,
            'eyebrow_raise': 0.0,
            'smile': 0.0,
            'breathing': 0.0,
            'eye_focus': 0.0
        }
        self.speech_queue = queue.Queue()
        self.current_text = ""
        self.load_realistic_avatar()
        
    def load_realistic_avatar(self):
        """Load realistic human avatar"""
        try:
            # Download realistic human photos
            if self.avatar_type == 'female':
                avatar_url = "https://i.pravatar.cc/400?img=5"
            elif self.avatar_type == 'male':
                avatar_url = "https://i.pravatar.cc/400?img=12"
            else:
                avatar_url = "https://i.pravatar.cc/400?img=1"
            
            response = requests.get(avatar_url, timeout=10)
            if response.status_code == 200:
                img_array = np.array(bytearray(response.content), dtype=np.uint8)
                self.face_image = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                self.face_image = cv2.resize(self.face_image, (400, 400))
                print(f"✅ Loaded realistic {self.avatar_type} avatar")
            else:
                self.create_fallback_avatar()
                
        except Exception as e:
            print(f"❌ Error loading avatar: {e}")
            self.create_fallback_avatar()
    
    def create_fallback_avatar(self):
        """Create fallback realistic avatar"""
        img = np.zeros((400, 400, 3), dtype=np.uint8)
        skin_color = (220, 190, 170) if self.avatar_type == 'female' else (200, 170, 150)
        
        # Face oval
        cv2.ellipse(img, (200, 200), (180, 220), 0, 0, 360, skin_color, -1)
        
        # Hair
        hair_color = (40, 30, 20) if self.avatar_type == 'female' else (30, 20, 10)
        cv2.ellipse(img, (200, 150), (200, 180), 0, 180, 360, hair_color, -1)
        
        # Eyes
        eye_color = (100, 60, 30)
        cv2.ellipse(img, (160, 180), (25, 15), 0, 0, 360, (255, 255, 255), -1)
        cv2.ellipse(img, (240, 180), (25, 15), 0, 0, 360, (255, 255, 255), -1)
        cv2.circle(img, (160, 180), 12, eye_color, -1)
        cv2.circle(img, (240, 180), 12, eye_color, -1)
        cv2.circle(img, (160, 180), 6, (0, 0, 0), -1)
        cv2.circle(img, (240, 180), 6, (0, 0, 0), -1)
        
        # Nose
        cv2.ellipse(img, (200, 220), (15, 20), 0, 0, 180, (180, 150, 130), -1)
        
        # Mouth
        cv2.ellipse(img, (200, 260), (30, 15), 0, 0, 180, (180, 100, 100), -1)
        
        self.face_image = img
        print("✅ Created fallback realistic avatar")
    
    def update_animation_state(self, gesture_intensity=50, is_speaking=False, text=""):
        """Update animation state berdasarkan input real-time"""
        t = time.time()
        
        # Speaking animation
        if is_speaking and text:
            self.current_text = text
            
            # Analisis text untuk mouth movement
            vowels = sum(1 for char in text.lower() if char in 'aeiou')
            consonants = sum(1 for char in text.lower() if char.isalpha() and char not in 'aeiou')
            
            # Mouth open berdasarkan vowels dan consonants
            if vowels > 0:
                self.animation_state['mouth_open'] = min(0.9, vowels / len(text) * 3)
            else:
                self.animation_state['mouth_open'] = 0.4
            
            # Eyebrow movement saat speaking
            self.animation_state['eyebrow_raise'] = 0.4 + np.sin(t * 6) * 0.3
            
            # Eye focus saat speaking
            self.animation_state['eye_focus'] = 0.8
        else:
            self.animation_state['mouth_open'] = 0.0
            self.animation_state['eyebrow_raise'] = 0.0
            self.animation_state['eye_focus'] = 0.0
        
        # Eye blinking
        if int(t * 2) % 8 == 0 and (t % 1) < 0.2:
            self.animation_state['eye_blink'] = 1.0
        else:
            self.animation_state['eye_blink'] = max(0, self.animation_state['eye_blink'] - 0.15)
        
        # Head movement berdasarkan gesture
        self.animation_state['head_tilt'] = np.sin(t * 0.5) * (gesture_intensity / 100.0) * 0.4
        
        # Breathing effect
        self.animation_state['breathing'] = np.sin(t * 0.8) * 0.08
        
        # Smile animation
        if gesture_intensity > 70:
            self.animation_state['smile'] = (gesture_intensity - 70) / 30.0
        else:
            self.animation_state['smile'] = 0.0
    
    def apply_facial_animations(self, face_img):
        """Apply facial animations ke face image"""
        h, w = face_img.shape[:2]
        center = (w//2, h//2)
        
        # Head tilt
        if self.animation_state['head_tilt'] != 0:
            angle = self.animation_state['head_tilt'] * 15
            M = cv2.getRotationMatrix2D(center, angle, 1.0)
            face_img = cv2.warpAffine(face_img, M, (w, h))
        
        # Breathing effect
        if self.animation_state['breathing'] != 0:
            scale = 1.0 + self.animation_state['breathing']
            M = cv2.getRotationMatrix2D(center, 0, scale)
            face_img = cv2.warpAffine(face_img, M, (w, h))
        
        # Eye blinking
        if self.animation_state['eye_blink'] > 0:
            eye_y = h - 220
            # Draw closed eyes
            cv2.line(face_img, (w//2 - 50, eye_y), (w//2 - 20, eye_y), (220, 190, 170), 4)
            cv2.line(face_img, (w//2 + 20, eye_y), (w//2 + 50, eye_y), (220, 190, 170), 4)
        else:
            # Normal eyes with focus
            eye_y = h - 220
            if self.animation_state['eye_focus'] > 0:
                # Focused eyes (slightly smaller pupils)
                cv2.circle(face_img, (w//2 - 40, eye_y), 8, (100, 60, 30), -1)
                cv2.circle(face_img, (w//2 + 40, eye_y), 8, (100, 60, 30), -1)
                cv2.circle(face_img, (w//2 - 40, eye_y), 4, (0, 0, 0), -1)
                cv2.circle(face_img, (w//2 + 40, eye_y), 4, (0, 0, 0), -1)
        
        # Mouth animation
        if self.animation_state['mouth_open'] > 0:
            mouth_y = h - 80
            mouth_width = int(30 + self.animation_state['mouth_open'] * 50)
            mouth_height = int(15 + self.animation_state['mouth_open'] * 25)
            
            # Draw open mouth
            cv2.ellipse(face_img, (w//2, mouth_y), (mouth_width, mouth_height), 
                       0, 0, 180, (100, 50, 50), -1)
            
            # Teeth
            if self.animation_state['mouth_open'] > 0.5:
                teeth_y = mouth_y - mouth_height//2
                cv2.rectangle(face_img, (w//2 - mouth_width//2, teeth_y), 
                            (w//2 + mouth_width//2, teeth_y + 8), (255, 255, 255), -1)
                
                # Tongue
                if self.animation_state['mouth_open'] > 0.7:
                    tongue_y = mouth_y - mouth_height//3
                    cv2.ellipse(face_img, (w//2, tongue_y), (mouth_width//2, mouth_height//3), 
                               0, 0, 180, (255, 150, 150), -1)
        
        # Smile animation
        if self.animation_state['smile'] > 0:
            smile_y = h - 90
            smile_width = int(40 + self.animation_state['smile'] * 30)
            cv2.ellipse(face_img, (w//2, smile_y), (smile_width, 12), 
                       0, 0, 180, (200, 100, 100), 4)
        
        # Eyebrow raise
        if self.animation_state['eyebrow_raise'] > 0:
            eyebrow_y = h - 250 - int(self.animation_state['eyebrow_raise'] * 15)
            cv2.ellipse(face_img, (w//2 - 60, eyebrow_y), (35, 10), 0, 0, 180, (40, 30, 20), -1)
            cv2.ellipse(face_img, (w//2 + 60, eyebrow_y), (35, 10), 0, 0, 180, (40, 30, 20), -1)
        
        return face_img
    
    def create_interactive_frame(self, gesture_intensity=50, is_speaking=False, text=""):
        """Create interactive frame dengan animasi real-time"""
        # Update animation state
        self.update_animation_state(gesture_intensity, is_speaking, text)
        
        # Portrait dimensions (9:16)
        frame = np.zeros((1920, 1080, 3), dtype=np.uint8)
        
        # Animated background
        t = time.time()
        for i in range(1920):
            color_r = int(40 + abs(np.sin((i + t * 20) / 200)) * 60)
            color_g = int(50 + abs(np.sin((i + t * 20 + 120) / 200)) * 70)
            color_b = int(80 + abs(np.sin((i + t * 20 + 240) / 200)) * 80)
            frame[i, :] = [color_b, color_g, color_r]
        
        if self.face_image is not None:
            # Resize face
            face_resized = cv2.resize(self.face_image, (600, 600))
            
            # Apply facial animations
            face_animated = self.apply_facial_animations(face_resized)
            
            # Position face
            y_offset = 300
            x_offset = 240
            frame[y_offset:y_offset+600, x_offset:x_offset+600] = face_animated
            
            # Add professional body
            self.add_professional_body(frame, x_offset, y_offset + 600)
        
        # Add UI overlays
        self.add_ui_overlays(frame, gesture_intensity, is_speaking, text)
        
        return frame
    
    def add_professional_body(self, frame, x_offset, y_start):
        """Add professional body"""
        # Neck
        neck_color = (200, 170, 150)
        cv2.rectangle(frame, (x_offset + 200, y_start), (x_offset + 400, y_start + 100), neck_color, -1)
        
        # Professional clothing
        clothing_color = (30, 30, 50)
        cv2.rectangle(frame, (x_offset + 100, y_start + 100), (x_offset + 500, y_start + 400), clothing_color, -1)
        cv2.ellipse(frame, (x_offset + 300, y_start + 100), (200, 80), 0, 0, 180, clothing_color, -1)
    
    def add_ui_overlays(self, frame, gesture_intensity, is_speaking, text):
        """Add UI overlays"""
        # Top status bar
        cv2.rectangle(frame, (0, 0), (1080, 80), (0, 0, 0), -1)
        cv2.rectangle(frame, (0, 0), (1080, 80), (37, 244, 238), 2)
        
        # Status text
        status_text = f"INTERACTIVE AVATAR | {self.avatar_type.upper()} | Gesture: {gesture_intensity}%"
        cv2.putText(frame, status_text, (30, 50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (37, 244, 238), 2)
        
        # Speaking indicator
        if is_speaking:
            cv2.circle(frame, (1020, 40), 20, (0, 255, 0), -1)
            cv2.putText(frame, "SPEAKING", (900, 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Show current text
            if text:
                display_text = text[:40] + "..." if len(text) > 40 else text
                cv2.putText(frame, f"'{display_text}'", (30, 1850), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        else:
            cv2.circle(frame, (1020, 40), 20, (100, 100, 100), -1)
        
        # Animation indicators
        cv2.putText(frame, f"Blink: {self.animation_state['eye_blink']:.1f}", (30, 1870), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(frame, f"Mouth: {self.animation_state['mouth_open']:.1f}", (200, 1870), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(frame, f"Smile: {self.animation_state['smile']:.1f}", (350, 1870), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(frame, f"Focus: {self.animation_state['eye_focus']:.1f}", (500, 1870), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    def speak(self, text, voice_type='female-1', speed=1.0, pitch=0):
        """Make avatar speak dengan animasi real-time"""
        self.is_speaking = True
        
        # Add to speech queue
        self.speech_queue.put({
            'text': text,
            'voice': voice_type,
            'speed': speed,
            'pitch': pitch,
            'start_time': time.time()
        })
        
        duration = len(text) / 10 * speed
        
        print(f"🗣️ Interactive Avatar speaking: {text}")
        print(f"   Voice: {voice_type}, Speed: {speed}x, Pitch: {pitch}")
        
        # Auto-stop speaking
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
    
    def process_frame(self, gesture_intensity=50, is_speaking=False, text=""):
        """Process frame dengan interaksi real-time"""
        return self.create_interactive_frame(gesture_intensity, is_speaking, text)


class StreamManager:
    """Manage interactive streaming sessions"""
    
    def __init__(self):
        self.streams = {}
        self.global_avatar = SimpleInteractiveAvatar('female')
    
    def create_stream(self, socket_id, settings):
        """Create new interactive stream"""
        avatar_type = settings.get('avatar', 'female')
        avatar = SimpleInteractiveAvatar(avatar_type)
        
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
        """Stop stream session"""
        if socket_id in self.streams:
            del self.streams[socket_id]
            return True
        return False
    
    def get_avatar(self):
        """Get global avatar"""
        return self.global_avatar
    
    def change_avatar(self, avatar_type):
        """Change global avatar"""
        self.global_avatar = SimpleInteractiveAvatar(avatar_type)
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
        'version': '3.0.0',
        'avatar_type': 'simple_interactive',
        'features': ['facial_animation', 'mouth_sync', 'eye_blink', 'head_movement', 'real_time_interaction', 'simple_deps']
    })


@app.route('/api/stream/start', methods=['POST'])
def start_stream():
    """Start interactive stream"""
    data = request.json
    socket_id = data.get('socketId')
    settings = data.get('settings', {})
    
    try:
        stream_manager.create_stream(socket_id, settings)
        
        return jsonify({
            'success': True,
            'message': 'Simple Interactive avatar stream started',
            'socket_id': socket_id,
            'features': ['Real-time facial animation', 'Mouth synchronization', 'Eye blinking', 'Head movement', 'Simple dependencies']
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/avatar/speak', methods=['POST'])
def avatar_speak():
    """Make interactive avatar speak"""
    data = request.json
    text = data.get('text', '')
    voice = data.get('voice', 'female-1')
    speed = float(data.get('speed', 1.0))
    pitch = int(data.get('pitch', 0))
    avatar_type = data.get('avatar', 'female')
    
    try:
        # Find active stream
        avatar = None
        for stream_data in stream_manager.streams.values():
            if stream_data['avatar'].avatar_type == avatar_type:
                avatar = stream_data['avatar']
                break
        
        if not avatar:
            avatar = SimpleInteractiveAvatar(avatar_type)
        
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
    """Change avatar type"""
    data = request.json
    avatar_type = data.get('avatar', 'female')
    
    try:
        stream_manager.change_avatar(avatar_type)
        
        return jsonify({
            'success': True,
            'message': f'Changed to simple interactive {avatar_type} avatar'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/frame/<socket_id>', methods=['GET'])
def get_frame(socket_id):
    """Get interactive avatar frame"""
    # For preview/non-stream, use global avatar
    if socket_id == 'avatar_stream':
        avatar = stream_manager.get_avatar()
    else:
        stream = stream_manager.get_stream(socket_id)
        if not stream:
            return jsonify({'error': 'Stream not found'}), 404
        avatar = stream['avatar']
    
    gesture_intensity = int(request.args.get('gesture', 50))
    is_speaking = request.args.get('speaking', 'false').lower() == 'true'
    text = request.args.get('text', '')
    
    frame = avatar.process_frame(gesture_intensity, is_speaking, text)
    
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
    
    if event == 'avatar_change':
        avatar_type = event_data.get('avatar', 'female')
        stream_manager.change_avatar(avatar_type)
    elif event == 'toggle_avatar':
        pass
    
    return jsonify({'success': True})


# WebSocket events
@socketio.on('connect')
def handle_connect():
    print('Simple Interactive Avatar client connected')


@socketio.on('disconnect')
def handle_disconnect():
    print('Simple Interactive Avatar client disconnected')


# Main
if __name__ == '__main__':
    print(f"🚀 Starting SIMPLE INTERACTIVE AVATAR Server on port {PORT}")
    print(f"👤 Real-time facial animation & interaction")
    print(f"🗣️ Mouth synchronization with speech")
    print(f"👀 Eye blinking & head movement")
    print(f"📱 Portrait Mode (9:16): 1080x1920")
    print(f"🎭 Avatar Types: Female, Male (Interactive)")
    print(f"🔗 Server ready at http://localhost:{PORT}")
    
    socketio.run(app, host='0.0.0.0', port=PORT, debug=False, allow_unsafe_werkzeug=True)
