import cv2
import numpy as np
import time
import pygame
import pygame.font
import random

from .audio_processor import AudioProcessor
from .ascii_converter import convert_to_ascii
from .character_sets import get_char_sets

def main():
    # Initialize webcam
    cap = cv2.VideoCapture(0)
    
    # Check if webcam opened successfully
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return
    
    # Initialize pygame
    pygame.init()
    
    # Initialize audio processor
    audio = AudioProcessor()
    
    # Reduced font size
    font_size = 6  # Small font size for detailed ASCII
    
    # Adjust ASCII dimensions
    ascii_width = 250
    ascii_height = 100
    
    font = pygame.font.SysFont('Courier New', font_size)
    
    # Calculate window size based on font dimensions
    char_width = font_size * 0.6  # Approximate width of a monospace character
    char_height = font_size
    
    window_width = int(ascii_width * char_width)
    window_height = int(ascii_height * char_height)
    
    # Create display window
    ascii_window = pygame.display.set_mode((window_width, window_height))
    pygame.display.set_caption("ASCII Video")
    
    # Background and text colors (lighter green theme)
    background_color = (5, 30, 5)  # Slightly lighter dark green
    text_color_bright = (20, 255, 60)  # Lighter bright green
    text_color_dim = (10, 150, 30)  # Lighter dim green
    
    char_sets = get_char_sets()
    
    # Current character set index
    current_set_index = 0
    
    # Time tracking for character set rotation
    last_rotation_time = time.time()
    rotation_interval = 5.0  # Rotate character set every 5 seconds
    
    # Status font (slightly larger for readability)
    status_font = pygame.font.SysFont('Courier New', 10)
    
    # Display calibration message
    print("Calibrating audio levels... Please stay quiet for a moment.")
    
    # Main loop
    running = True
    while running:
        current_time = time.time()
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    running = False
                elif event.key == pygame.K_SPACE:
                    # Manual character set rotation
                    current_set_index = (current_set_index + 1) % len(char_sets)
                elif event.key == pygame.K_r:
                    # Recalibrate audio
                    audio.is_calibrating = True
                    audio.calibration_count = 0
                    print("Recalibrating audio... Please stay quiet for a moment.")
        
        # Automatic character set rotation
        if current_time - last_rotation_time > rotation_interval:
            current_set_index = (current_set_index + 1) % len(char_sets)
            last_rotation_time = current_time
        
        # Get the current audio level
        audio_level = audio.get_level()
        
        # Capture frame-by-frame
        ret, frame = cap.read()
        
        if not ret:
            print("Error: Failed to capture image")
            break
        
        # Mirror the frame horizontally for a more intuitive view
        frame = cv2.flip(frame, 1)
        
        # Convert frame to ASCII
        ascii_frame = convert_to_ascii(frame, ascii_width, ascii_height, char_sets[current_set_index])
        
        # Clear the window with dark green background
        ascii_window.fill(background_color)
        
        # Get base green value influenced by audio level (pulsing effect)
        base_brightness = 0.7 + 0.3 * audio_level  # Increases brightness based on audio
        
        # Render ASCII art to the window with green text
        for i, row in enumerate(ascii_frame):
            for j, char in enumerate(row):
                x_pos = int(j * char_width)
                y_pos = int(i * char_height)
                
                # Determine brightness based on character position in the set
                char_index = char_sets[current_set_index].find(char)
                char_brightness = 1.0 - (char_index / len(char_sets[current_set_index]))
                
                # Apply audio-reactive pulsing
                brightness = char_brightness * base_brightness
                
                # Interpolate between dim and bright green based on brightness
                green_value = int(text_color_dim[1] + brightness * (text_color_bright[1] - text_color_dim[1]))
                red_value = int(text_color_dim[0] + brightness * (text_color_bright[0] - text_color_dim[0]))
                blue_value = int(text_color_dim[2] + brightness * (text_color_bright[2] - text_color_dim[2]))
                
                current_color = (red_value, green_value, blue_value)
                
                # Apply subtle movement based on audio for characters
                jitter_x = 0
                jitter_y = 0
                if audio_level > 0.5:  # Only jitter on louder sounds
                    jitter_amount = int(audio_level * 2)
                    jitter_x = random.randint(-jitter_amount, jitter_amount)
                    jitter_y = random.randint(-jitter_amount, jitter_amount)
                
                char_surface = font.render(char, True, current_color)
                ascii_window.blit(char_surface, (x_pos + jitter_x, y_pos + jitter_y))
        
        # Display character set info with slightly larger font for readability
        if audio.is_calibrating:
            status_text = "Calibrating audio... Please stay quiet"
        else:
            status_text = f"Set: {current_set_index+1}/{len(char_sets)} | Audio: {int(audio_level*100)}% | Space: change set | R: recalibrate"
        
        status_surface = status_font.render(status_text, True, (200, 255, 200))
        ascii_window.blit(status_surface, (10, window_height - 20))
        
        # Update the display
        pygame.display.flip()
        
        # Display the original frame in a window
        cv2.imshow('Original Video', frame)
        
        # Check for OpenCV 'q' key press (as backup)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # Clean up
    audio.cleanup()
    cap.release()
    cv2.destroyAllWindows()
    pygame.quit()

if __name__ == "__main__":
    main()
