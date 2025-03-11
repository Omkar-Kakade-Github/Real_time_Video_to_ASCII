
def get_char_sets():
    """
    Returns a list of different character sets for ASCII art rendering.
    Each set is ordered from darkest to lightest characters.
    
    Returns:
        list: List of character set strings
    """
    return [
        '@%#*+=-:. ',                # Standard set
        '$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~<>i!lI;:,"^`\'. ',  # Detailed set
        '░▒▓█▚▞▙▟▀▄▐▌▝▘▗▖',          # Block elements
        '◈◇◆◉●◍◎◌○◯◐◑◒◓◔◕◖◗',        # Geometric shapes
        '♠♣♥♦♤♧♡♢♩♪♫♬♭♮♯',            # Card suits and music
        '01'                         # Binary
    ]
