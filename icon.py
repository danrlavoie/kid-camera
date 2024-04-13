import random
import pygame

def get_random_color():
    r = random.randInt(150,255)
    g = random.randInt(150,255)
    b = random.randInt(150,255)
    return (r,g,b)

def get_icon(filepath, rgb=None,alpha=None, position=None):
    """
    get_icon takes a filepath, an optional RGB color tuple, and an optional alpha
    value from 0 to 255. It returns a pygame image of the file, set to the
    specified color and transparency, suitable for blitting to the screen.
    """
    icon = pygame.image.load(filepath)
    if (rgb is None):
        rgb = get_random_color()
    if (alpha is None):
        alpha = 255
    rgba = rgb + alpha
    icon = icon.fill(rgba, special_flags=pygame.BLEND_ADD)
    if (position == "topleft"):
        icon = pygame.transform.scale(icon, (80, 80))
        return [icon, (0,0)]
    elif (position == "topright"):
        icon = pygame.transform.scale(icon, (80, 80))
        return [icon, (560, 0)]
    elif (position == "bottomleft"):
        icon = pygame.transform.scale(icon, (80, 80))
        return [icon, (0, 400)]
    elif (position == "bottomright"):
        icon = pygame.transform.scale(icon, (80, 80))
        return [icon, (560, 400)]
    else: # (position == "center"):
        icon = pygame.transform.scale(icon, (480,480))
        # Center the icon on the screen by placing upper left so it aligns to center
        # (640 - 480) / 2 = 80
        return [icon, (80,0)]

