import os
import base64
from io import BytesIO
from typing import Optional
import tempfile

# Try imports with fallbacks
try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False
    print("Warning: pyttsx3 not available")

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False
    print("Warning: gTTS not available")


class TextToSpeech:
    def __init__(self):
        self.use_gtts = GTTS_AVAILABLE  # Use gTTS if available
        self._init_engine()
        print(f"TTS initialized: gTTS={GTTS_AVAILABLE}, pyttsx3={PYTTSX3_AVAILABLE}")
    
    def _init_engine(self):
        """Initialize TTS engine"""
        self.engine = None
        
        if PYTTSX3_AVAILABLE:
            try:
                # Try to initialize pyttsx3 as fallback
                self.engine = pyttsx3.init()
                self.engine.setProperty('rate', 150)  # Speed
                self.engine.setProperty('volume', 0.8)  # Volume
                
                # Try to set a professional voice
                voices = self.engine.getProperty('voices')
                if voices:
                    # Prefer female voice for interviewer
                    for voice in voices:
                        if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                            self.engine.setProperty('voice', voice.id)
                            break
                print("✓ pyttsx3 engine initialized")
            except Exception as e:
                print(f"pyttsx3 initialization error: {e}")
                self.engine = None
        else:
            print("pyttsx3 not available")
    
    def speak_text(self, text: str) -> Optional[str]:
        """Convert text to speech and return base64 audio data"""
        if not text.strip():
            return None
        
        print(f"Generating speech for: {text[:50]}...")
        
        try:
            if self.use_gtts and GTTS_AVAILABLE:
                result = self._speak_with_gtts(text)
                if result:
                    print("✓ gTTS speech generated")
                    return result
                else:
                    print("gTTS failed, trying pyttsx3...")
            
            if PYTTSX3_AVAILABLE and self.engine:
                result = self._speak_with_pyttsx3(text)
                if result:
                    print("✓ pyttsx3 speech generated")
                    return result
                else:
                    print("pyttsx3 failed")
            
            print("❌ All TTS methods failed")
            return None
            
        except Exception as e:
            print(f"TTS error: {e}")
            return None
    
    def _speak_with_gtts(self, text: str) -> Optional[str]:
        """Use Google Text-to-Speech"""
        try:
            # Create TTS object
            tts = gTTS(text=text, lang='en', slow=False)
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
                tts.save(tmp_file.name)
                
                # Read file and convert to base64
                with open(tmp_file.name, 'rb') as f:
                    audio_data = f.read()
                
                # Clean up temp file
                os.unlink(tmp_file.name)
                
                # Convert to base64
                audio_base64 = base64.b64encode(audio_data).decode('utf-8')
                return f"data:audio/mp3;base64,{audio_base64}"
                
        except Exception as e:
            print(f"gTTS error: {e}")
            return None
    
    def _speak_with_pyttsx3(self, text: str) -> Optional[str]:
        """Use pyttsx3 for offline TTS"""
        try:
            if not self.engine:
                return None
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
                self.engine.save_to_file(text, tmp_file.name)
                self.engine.runAndWait()
                
                # Read file and convert to base64
                with open(tmp_file.name, 'rb') as f:
                    audio_data = f.read()
                
                # Clean up temp file
                os.unlink(tmp_file.name)
                
                # Convert to base64
                audio_base64 = base64.b64encode(audio_data).decode('utf-8')
                return f"data:audio/wav;base64,{audio_base64}"
                
        except Exception as e:
            print(f"pyttsx3 error: {e}")
            return None
    
    def get_available_voices(self) -> list:
        """Get list of available voices"""
        if not self.engine:
            return []
        
        voices = self.engine.getProperty('voices')
        return [{'id': voice.id, 'name': voice.name} for voice in voices] if voices else []
    
    def set_voice(self, voice_id: str) -> bool:
        """Set specific voice"""
        if not self.engine:
            return False
        
        try:
            self.engine.setProperty('voice', voice_id)
            return True
        except Exception:
            return False
    
    def set_rate(self, rate: int) -> bool:
        """Set speech rate (words per minute)"""
        if not self.engine:
            return False
        
        try:
            self.engine.setProperty('rate', rate)
            return True
        except Exception:
            return False
    
    def set_volume(self, volume: float) -> bool:
        """Set volume (0.0 to 1.0)"""
        if not self.engine:
            return False
        
        try:
            self.engine.setProperty('volume', max(0.0, min(1.0, volume)))
            return True
        except Exception:
            return False
