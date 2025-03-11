import cv2
import numpy as np

def convert_to_ascii(image, width, height, char_set):
    """Convert an image to ASCII art using the provided character set."""
    # Resize the image
    resized = cv2.resize(image, (width, height))
    
    # Convert to grayscale
    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    
    # Map grayscale values to ASCII characters
    ascii_map = np.zeros(gray.shape, dtype=str)
    for i in range(height):
        for j in range(width):
            # Map pixel value (0-255) to index in char_set
            ascii_index = int(gray[i, j] / 255 * (len(char_set) - 1))
            ascii_map[i, j] = char_set[ascii_index]
    
    return ascii_map
