import pygame
from pygame.locals import *
import os
import time
import RPi.GPIO as GPIO
import sys
import json

# Color definitions
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Environment variables setup
os.putenv('SDL_VIDEODRV', 'fbcon')
os.putenv('SDL_FBDEV', '/dev/fb0')
os.putenv('SDL_MOUSEDRV', 'dummy')
os.putenv('SDL_MOUSEDEV', '/dev/null')
os.putenv('DISPLAY', '')

# Initialize Pygame
pygame.init()
pygame.mouse.set_visible(False)

screen = pygame.display.set_mode((320, 240))
screen.fill(BLACK)
pygame.display.update()

large_font = pygame.font.Font(None, 120)
small_font = pygame.font.Font(None, 24)

#Initialize GPIO and event detection
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def GPIO_17_callback_quit(channel):
    GPIO.cleanup()
    pygame.quit()
    sys.exit()

# Add GPIO event detection
GPIO.add_event_detect(17, GPIO.FALLING, callback=GPIO_17_callback_quit, bouncetime=300)

# get arrow symbol based on instruction and current heading
def get_arrow_symbol(instruction, current_heading, is_moving):
    instruction = instruction.lower()
        
    # Handle turn instructions
    if 'turn' in instruction:
        if 'turn right' in instruction:
            return '→'
        if 'turn left' in instruction:
            return '←'
        if 'slight right' in instruction:
            return '↗'
        if 'slight left' in instruction:
            return '↖'
        if 'sharp right' in instruction:
            return '→'
        if 'sharp left' in instruction:
            return '←'
        if 'u-turn' in instruction:
            return '↓'
        
    # Handle heading instructions
    if 'head' in instruction:
        # If not moving, use default compass directions
        if not is_moving:
            if 'north' in instruction:
                return '↑'
            if 'south' in instruction:
                return '↓'
            if 'east' in instruction:
                return '→'
            if 'west' in instruction:
                return '←'
            if 'northeast' in instruction:
                return '↗'
            if 'northwest' in instruction:
                return '↖'
            if 'southeast' in instruction:
                return '↘'
            if 'southwest' in instruction:
                return '↙'
                
        else:
            # Use heading calculation when moving
            direction_to_degrees = {
                'north': 0,
                'northeast': 45,
                'east': 90,
                'southeast': 135,
                'south': 180,
                'southwest': 225,
                'west': 270,
                'northwest': 315
            }
                
            # Extract target direction
            target_degrees = None
            for direction, degrees in direction_to_degrees.items():
                if f"head {direction}" in instruction:
                    target_degrees = degrees
                    break
            
            #calculate angle difference
            if target_degrees is not None:
                # Calculate angle difference
                angle_diff = (target_degrees - current_heading) % 360
                
                # Convert angle to arrow
                if angle_diff <= 22.5 or angle_diff > 337.5:
                    return '↑'
                elif 22.5 < angle_diff <= 67.5:
                    return '↗'
                elif 67.5 < angle_diff <= 112.5:
                    return '→'
                elif 112.5 < angle_diff <= 157.5:
                    return '↘'
                elif 157.5 < angle_diff <= 202.5:
                    return '↓'
                elif 202.5 < angle_diff <= 247.5:
                    return '↙'
                elif 247.5 < angle_diff <= 292.5:
                    return '←'
                elif 292.5 < angle_diff <= 337.5:
                    return '↖'
        
    return '↑'  # Default arrow

def display_navigation_info(nav_info):
    # display distance
    distance_text = small_font.render(
        f"Next: {nav_info.get('distance', 'N/A')}", 
        True, WHITE
    )
    screen.blit(distance_text, (10, 160))
    
    # Display total distance
    total_distance_text = small_font.render(
        f"Total: {nav_info.get('total_distance', 'N/A')}", 
        True, WHITE
    )
    screen.blit(total_distance_text, (10, 240 - 55))
    
    # show time
    duration_text = small_font.render(
        f"ETA: {nav_info.get('duration', 'N/A')}", 
        True, WHITE
    )
    screen.blit(duration_text, (10, 210))

def display_navigation(nav_data):

    screen.fill(BLACK)
            
    #Get navigation and GPS data
    nav_info = nav_data.get('navigation', {})
    gps_info = nav_data.get('gps', {})
            
    #for instruction
    instruction = nav_info.get('instruction', '')
    instruction = instruction.replace('<', '').replace('>', '')
        
    #Get GPS data
    current_heading = float(gps_info.get('current_heading', 0.0))
    is_moving = gps_info.get('is_moving', False)
        
    # Calculate and display arrow
    arrow = get_arrow_symbol(instruction, current_heading, is_moving)

    #Display arrow
    arrow_text = large_font.render(arrow, True, WHITE)
    arrow_x = (320 - arrow_text.get_width()) // 2
    arrow_y = (240 - arrow_text.get_height()) // 2 - 60
    screen.blit(arrow_text, (arrow_x, arrow_y))
            
    # Display navigation info
    display_navigation_info(nav_info)
            
    pygame.display.flip()


def check_navigation_data():
    #check navigation data
    nav_file = os.path.join(os.path.dirname(__file__), 'navigation_data.json')
    if os.path.exists(nav_file):
        with open(nav_file, 'r') as f:
            nav_data = json.load(f)
            display_navigation(nav_data)


def cleanup():
    #clean up GPIO and pygame
    GPIO.cleanup()
    pygame.quit()

def main():
    try:
        # Main loop
        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    cleanup()
                    sys.exit()
                
            # Check navigation data updates
            check_navigation_data()
                
            time.sleep(1)
                
    except KeyboardInterrupt:
        print("\nExiting...")

    finally:
        cleanup()

if __name__ == "__main__":
    main()




