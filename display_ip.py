import pygame
import time
import subprocess
import os
from pygame.locals import *

# Set environment variables for PiTFT
os.putenv('SDL_VIDEODRV', 'fbcon')
os.putenv('SDL_FBDEV', '/dev/fb0')
os.putenv('SDL_MOUSEDRV', 'dummy')
os.putenv('SDL_MOUSEDEV', '/dev/null')
os.putenv('DISPLAY', '')

#Initialize colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

#Initialize Pygame
pygame.init()
pygame.mouse.set_visible(False)

screen = pygame.display.set_mode((320, 240))
pygame.display.set_caption('IP Display')

# Set up font
font = pygame.font.Font(None, 24)

def get_ip_address():

    # Run the ip address command and capture corresponding output
    cmd = "ip addr show | grep 'inet ' | grep -v '127.0.0.1' | awk '{print $2}' | cut -d/ -f1"
    ip_output = subprocess.check_output(cmd, shell=True).decode('utf-8').strip()
        
    if ip_output:
        return ip_output.split('\n')
    return ["No IP found"]
    

def main():
    try:

        # Clear the screen
        screen.fill(BLACK)

        #For IP addresses
        ip_addresses = get_ip_address()

        # Display IP addresses
        y_position = 80
        screen.blit(font.render("IP Addresses:", True, WHITE), (20, 40))
        
        for ip in ip_addresses:
            text = font.render(ip, True, WHITE)
            screen.blit(text, (20, y_position))
            y_position += 30

        #Update the display
        pygame.display.flip()

        # Wait for 30 seconds
        time.sleep(30)

    finally:
        pygame.quit()

if __name__ == "__main__":
    main() 
