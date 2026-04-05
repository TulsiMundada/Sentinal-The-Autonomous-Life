import time
import os

def clear_console():
    # Clears terminal for animation effect
    os.system('cls' if os.name == 'nt' else 'clear')

def draw_text_heart():
    # The mathematical heart curve: (x^2 + y^2 - 1)^3 - x^2 * y^3 = 0
    heart_frame = ""
    for y in range(15, -15, -1):
        line = ""
        for x in range(-30, 30):
            # Scaling the coordinates to fit the terminal aspect ratio
            if ((x * 0.05)**2 + (y * 0.1)**2 - 1)**3 - (x * 0.05)**2 * (y * 0.1)**3 <= 0:
                line += "❤️"
            else:
                line += "  "
        heart_frame += line + "\n"
    
    # Simple "typing" animation for the message
    message = "  [ System Status: Loving You... 100% ]  "
    
    clear_console()
    print(heart_frame)
    print(message.center(60))

if __name__ == "__main__":
    try:
        draw_text_heart()
    except KeyboardInterrupt:
        print("\nProcess interrupted, but the love remains.")