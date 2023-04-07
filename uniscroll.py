import time
import threading
import queue
import random
import logging
import unicornhat as uh
import sys
from flask import Flask, request, render_template, redirect, url_for, flash

# Suppress flask messages
cli = sys.modules['flask.cli']
cli.show_server_banner = lambda *x: None

uh.set_layout(uh.PHAT)
uh.brightness(0.5)
uh.set_layout(uh.PHAT)
uh.brightness(0.5)

last_displayed_text = "Hellody Everyone!"
input_queue = queue.Queue()

log = logging.getLogger("werkzeug")
log.setLevel(logging.ERROR)

font = {
    'A': [[0, 1, 0], [1, 0, 1], [1, 1, 1], [1, 0, 1]],
    'B': [[1, 1, 0], [1, 0, 1], [1, 1, 0], [1, 0, 1]],
    'C': [[0, 1, 1], [1, 0, 0], [1, 0, 0], [0, 1, 1]],
    'D': [[1, 1, 0], [1, 0, 1], [1, 0, 1], [1, 1, 0]],
    'E': [[1, 1, 1], [1, 0, 1], [1, 1, 0], [1, 1, 1]],
    'F': [[1, 1, 1], [1, 0, 0], [1, 1, 0], [1, 0, 0]],
    'G': [[0, 1, 1], [1, 0, 0], [1, 0, 1], [0, 1, 1]],
    'H': [[1, 0, 1], [1, 0, 1], [1, 1, 1], [1, 0, 1]],
    'I': [[1, 1, 1], [0, 1, 0], [0, 1, 0], [1, 1, 1]],
    'J': [[0, 1, 1], [0, 0, 1], [1, 0, 1], [0, 1, 0]],
    'K': [[1, 0, 1], [1, 1, 0], [1, 0, 1], [1, 0, 1]],
    'L': [[1, 0, 0], [1, 0, 0], [1, 0, 0], [1, 1, 1]],
    'M': [[1, 0, 0, 0, 1],
          [1, 1, 1, 1, 1],
          [1, 0, 1, 0, 1],
          [1, 0, 1, 0, 1]],
    'N': [[1, 0, 0, 1],
          [1, 1, 0, 1],
          [1, 0, 1, 1],
          [1, 0, 0, 1]],
    'O': [[0, 1, 0], [1, 0, 1], [1, 0, 1], [0, 1, 0]],
    'P': [[1, 1, 0], [1, 0, 1], [1, 1, 0], [1, 0, 0]],
    'Q': [[0, 1, 0], [1, 0, 1], [1, 0, 1], [0, 1, 1]],
    'R': [[1, 1, 0], [1, 0, 1], [1, 1, 0], [1, 0, 1]],
    'S': [[1, 1, 1, 1],
          [1, 1, 0, 0],
          [0, 0, 1, 1],
          [1, 1, 1, 1]],
    'T': [[1, 1, 1], [0, 1, 0], [0, 1, 0], [0, 1, 0]],
    'U': [[1, 0, 1], [1, 0, 1], [1, 0, 1], [0, 1, 0]],
    'V': [[1, 0, 1], [1, 0, 1], [1, 0, 1], [0, 1, 0]],
    'W': [[1, 0, 0, 0, 1],
          [1, 0, 1, 0, 1],
          [1, 1, 0, 1, 1],
          [1, 0, 0, 0, 1]],
    'X': [[1, 0, 1], [0, 1, 0], [0, 1, 0], [1, 0, 1]],
    'Y': [[1, 0, 1], [0, 1, 0], [0, 1, 0], [0, 1, 0]],
    'Z': [[1, 1, 1], [0, 0, 1], [0, 1, 0], [1, 1, 1]],
    '0': [[0, 1, 0], [1, 1, 1], [1, 1, 1], [0, 1, 0]],
    '1': [[0, 1, 0], [1, 1, 0], [0, 1, 0], [0, 1, 0]],
    '2': [[1, 1, 0], [0, 0, 1], [0, 1, 0], [1, 1, 1]],
    '3': [[1, 1, 0], [0, 0, 1], [0, 1, 0], [1, 0, 1]],
    '4': [[1, 0, 1], [1, 0, 1], [1, 1, 1], [0, 0, 1]],
    '5': [[1, 1, 1], [1, 0, 0], [1, 1, 0], [1, 1, 1]],
    '6': [[0, 1, 1], [1, 0, 0], [1, 1, 0], [0, 1, 1]],
    '7': [[1, 1, 1], [0, 0, 1], [0, 1, 0], [1, 0, 0]],
    '8': [[0, 1, 0], [1, 0, 1], [0, 1, 0], [1, 0, 1]],
    '9': [[0, 1, 1], [1, 0, 1], [0, 1, 1], [1, 0, 0]],
    '?': [[0, 1, 0], [1, 0, 1], [0, 0, 1], [0, 1, 0]],
    ' ': [[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]],
    '.': [[0], [0], [0], [1]],
    ',': [[0], [0], [0], [1], [1]],
    '!': [[0, 1, 0], [0, 1, 0], [0, 0, 0], [0, 1, 0]],
    ':': [[0], [1], [0], [1]]
}

# init flask web service
app = Flask(__name__)
app.secret_key = "a1b2c3d4e5f6g7h8i9j0"

@app.route('/input', methods=['POST'])
def web_input():
    text = request.form['text']
    global input_queue
    text = request.form.get('text')
    if text:
        input_queue.put(text)
        flash(f'Message sent to picorn: {text}')
    return redirect(url_for('index'))

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

def lerp_color(color1, color2, t):
    r1, g1, b1 = color1
    r2, g2, b2 = color2
    r = int(r1 * (1 - t) + r2 * t)
    g = int(g1 * (1 - t) + g2 * t)
    b = int(b1 * (1 - t) + b2 * t)
    return (r, g, b)

def draw_char(char, x_offset, y_offset, color):
    char_data = font.get(char.upper(), [[0]])  # Fallback to a single pixel if the character is not in the font
    for x, row in enumerate(char_data):
        for y, value in enumerate(row):
            if value:
                uh.set_pixel(x + x_offset, y + y_offset, *color)

def draw_scroll_data(scroll_data, offset):
    for x in range(8):
        for y in range(4):
            col_idx = x - offset
            if 0 <= col_idx < len(scroll_data) and 0 <= y < len(scroll_data[col_idx]):
                r, g, b = scroll_data[col_idx][y]
                uh.set_pixel(x, y, r, g, b)
            else:
                uh.set_pixel(x, y, 0, 0, 0)

def scroll_text(text):
    scroll_data = []

    color1 = (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
    color2 = (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
    
    for ch in text.upper():
        if ch in font:
            ch_data = font[ch]
            for col_idx in range(len(ch_data[0])):
                col = [row[col_idx] for row in ch_data]
                t = col_idx / len(ch_data[0])
                color = lerp_color(color1, color2, t)
                scroll_data.append([(color[0]*v, color[1]*v, color[2]*v) for v in col])
            scroll_data.append([(0, 0, 0)] * len(ch_data))  # Add space after each letter
        color1 = color2
        color2 = (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))

    for offset in range(8, -len(scroll_data), -1):
        draw_scroll_data(scroll_data, offset)
        uh.show()
        time.sleep(0.1)
    
    # Return the length of the scroll_data
    return len(scroll_data)

def input_handler():
    global input_queue
    while True:
        text = input("Enter a word or sentence: ")
        input_queue.put(text)

def main(input_queue):
    global last_displayed_text
    # Start a thread to handle user input
    input_thread = threading.Thread(target=input_handler)
    input_thread.daemon = True
    input_thread.start()

    # Start scrolling the text
    scroll_text(last_displayed_text)

    while True:
        if not input_queue.empty():
            new_text = input_queue.get()
            last_displayed_text = new_text
            scroll_data_length = scroll_text(new_text)
        else:
            # Continue scrolling the last displayed text with three spaces in between the loop
            scroll_text(" " * 3 + last_displayed_text)

if __name__ == "__main__":
    input_queue = queue.Queue()

    # Start a thread for the main loop
    main_thread = threading.Thread(target=main, args=(input_queue,))
    main_thread.daemon = True
    main_thread.start()

    # Start the Flask web server
    app.run(host='0.0.0.0', port=5000)
