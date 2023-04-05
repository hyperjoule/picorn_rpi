import time
import random
import unicornhat as uh

uh.set_layout(uh.PHAT)
uh.brightness(0.5)

# Set the color of a specific LED
def set_pixel(x, y, r, g, b):
    uh.set_pixel(x, y, r, g, b)

# Clear the pHAT
def clear():
    uh.clear()

# Show the current state of the pHAT
def show():
    uh.show()

# Fade a color in and out
def fade_color(r, g, b, duration):
    min_brightness = 100  # Minimum brightness value (0-255)

    for i in range(min_brightness, 255, 5):
        uh.brightness(i / 255)
        fill(r, g, b)
        show()
        time.sleep(duration / 100)

    for i in range(255, min_brightness, -5):
        uh.brightness(i / 255)
        fill(r, g, b)
        show()
        time.sleep(duration / 100)

# Fill the pHAT with a color
def fill(r, g, b):
    for x in range(8):
        for y in range(4):
            set_pixel(x, y, r, g, b)
    show()

# Display random colors and patterns
def random_pattern():
    for _ in range(50):
        x = random.randint(0, 7)
        y = random.randint(0, 3)
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        set_pixel(x, y, r, g, b)
        show()
        time.sleep(0.05)

while True:
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)

    fade_color(r, g, b, 5)
    random_pattern()
