import pyaudio
import struct
import threading
import math
import time

class AudioProcessor:
    def __init__(self):
        self.audio_level = 0
        self.running = True
        self.chunk_size = 1024
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 44100
        
        # Calibration variables
        self.noise_floor = 500  # Initial estimate of background noise
        self.calibration_samples = 10
        self.calibration_count = 0
        self.is_calibrating = True
        self.max_level_seen = 1000  # Initial estimate for scaling
        
        # Start audio capture in a separate thread
        self.audio_thread = threading.Thread(target=self._process_audio)
        self.audio_thread.daemon = True
        self.audio_thread.start()
    
    def _process_audio(self):
        """Continuously process audio input to calculate volume level"""
        p = pyaudio.PyAudio()
        stream = p.open(format=self.format,
                        channels=self.channels,
                        rate=self.rate,
                        input=True,
                        frames_per_buffer=self.chunk_size)
        
        # Wait a moment for mic to initialize
        time.sleep(0.5)
        
        while self.running:
            try:
                # Read audio data
                data = stream.read(self.chunk_size, exception_on_overflow=False)
                # Convert to numeric values
                count = len(data) // 2
                format = f"{count}h"
                shorts = struct.unpack(format, data)
                
                # Calculate volume (RMS of the samples)
                sum_squares = sum(s * s for s in shorts)
                rms = math.sqrt(sum_squares / count)
                
                # Calibration phase: determine noise floor
                if self.is_calibrating:
                    self.calibration_count += 1
                    # Update noise floor estimate (running average)
                    self.noise_floor = (self.noise_floor * (self.calibration_count - 1) + rms) / self.calibration_count
                    
                    if self.calibration_count >= self.calibration_samples:
                        # Add 20% margin to noise floor
                        self.noise_floor *= 1.2
                        self.is_calibrating = False
                        print(f"Audio calibration complete. Noise floor: {self.noise_floor:.1f}")
                else:
                    # Update max level if needed for dynamic range
                    if rms > self.max_level_seen and rms < 20000:  # Avoid outliers
                        self.max_level_seen = rms
                
                # Apply noise gate - subtract noise floor and clamp to zero minimum
                adjusted_rms = max(0, rms - self.noise_floor)
                
                # Calculate dynamic range for normalization
                effective_range = self.max_level_seen - self.noise_floor
                
                # Prevent division by zero or too small values
                if effective_range < 100:
                    effective_range = 100
                
                # Normalize to 0-1 range with dynamic scaling
                normalized = min(1.0, adjusted_rms / effective_range)
                
                # Apply exponential curve to make it less sensitive to small sounds
                normalized = normalized ** 1.5
                
                # Apply smoothing for more natural transitions
                self.audio_level = self.audio_level * 0.8 + normalized * 0.2
                
            except Exception as e:
                print(f"Audio processing error: {e}")
                time.sleep(0.1)
        
        # Clean up
        stream.stop_stream()
        stream.close()
        p.terminate()
    
    def get_level(self):
        """Return the current audio level (0-1)"""
        if self.is_calibrating:
            return 0.0  # No audio reactivity during calibration
        return self.audio_level
    
    def cleanup(self):
        """Stop the audio processing thread"""
        self.running = False
        if self.audio_thread.is_alive():
            self.audio_thread.join(timeout=1.0)
