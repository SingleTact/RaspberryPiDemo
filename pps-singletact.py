#!/usr/bin/env python
# PPS SingleTact Demo
# Written by Ardhan Madras <ardhan@rocksis.net>
#

from gi.repository import Gtk, GLib, Gdk
import cairo
import sys
import math
import time
import random
import threading

DEVICE_ENABLED = False
try:
    import smbus
    DEVICE_ENABLED = True
except ImportError:
    pass


WINDOW_WIDTH = 800
WINDOW_HEIGHT = 480
GRAPH_WIDTH = WINDOW_WIDTH - 75
GRAPH_HEIGHT = WINDOW_HEIGHT - 120
GRAPH_X_START = 65
GRAPH_Y_START = 10
INTERVAL = 100 # In ms
ELAPSED_TIME = 0 # In ms

SECONDS = []
SECOND_MAX = 30
SECOND_SPACE = GRAPH_WIDTH / float(SECOND_MAX)

CURVES = []
CURVE_MAX = SECOND_MAX * (1000 / INTERVAL)
CURVE_SPACE = GRAPH_WIDTH / float(CURVE_MAX)

VALUE_MAX = 760
VALUE_MIN = -240
VALUE_STEP = 20
VALUE_SPACE = 50

READ_THREAD = None
THREAD_IS_RUN = False
KEY_IS_PRESSED = False
TOUCH_BEGIN = False
TOUCH_TIME = 0

DEV_BUS = 1
DEV_ADDRESS = 0x04

OPT_VERBOSE = False

# Calculate Y position based on pressure value
value_pos = lambda value: GRAPH_Y_START + ((VALUE_MAX - value) / float(VALUE_STEP) \
                          * GRAPH_HEIGHT / float(VALUE_SPACE))

# Draw callback
# Don't do any time related calculation here!
def drawing_draw_cb(widget, cr, *args):

    # Outmost rectangle
    cr.set_source_rgb(0x00, 0x00, 0x00)
    cr.set_line_width (2)
    cr.rectangle(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
    cr.stroke()

    cr.rectangle(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
    cr.set_source_rgb(0xff, 0xff, 0xff)
    cr.fill()

    # Output text
    cr.set_source_rgb(0x00, 0x00, 0x00)
    cr.select_font_face('Roboto', cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    cr.set_font_size(12)
    text = 'OUTPUT (512 = FULL SCALE RANGE)'
    ext = cr.text_extents(text)
    cr.move_to(8 + ext[3], GRAPH_Y_START + GRAPH_HEIGHT / 2 + ext[2] / 2)
    cr.rotate(-90 * (math.pi / 180))
    cr.show_text(text)
    cr.stroke()

    cr.rotate(90 * (math.pi / 180))

    # Graph rectangle
    cr.set_source_rgb(0x00, 0x00, 0x00)
    cr.set_line_width (1.0)
    cr.rectangle(GRAPH_X_START, GRAPH_Y_START, GRAPH_WIDTH, GRAPH_HEIGHT)
    cr.stroke()

    # Y scale and value label
    # End with VALUE_MAX
    cr.select_font_face('Roboto', cairo.FONT_SLANT_NORMAL)
    cr.set_font_size(12)
    x_pos, y_pos = GRAPH_X_START, GRAPH_Y_START
    value = VALUE_MAX
    while value >= VALUE_MIN:
        cr.set_line_width (0.5)
        # Y scale
        if value % 100 == 0:
            # Left Y scale
            cr.move_to(x_pos - 6, y_pos)
            cr.line_to(x_pos + 6, y_pos)
            # Right Y scale
            cr.set_line_width (0.5)
            cr.move_to(GRAPH_X_START + GRAPH_WIDTH, y_pos)
            cr.line_to(GRAPH_X_START + GRAPH_WIDTH - 6, y_pos)
            cr.stroke()
            # Labels
            ext = cr.text_extents(str(value))
            cr.move_to(x_pos - (22 + ext[2] / 2) , y_pos + ext[3] / 2)
            cr.set_source_rgb(0x00, 0x00, 0x00)
            cr.show_text(str(value))

            # Line from left to right
            cr.move_to(GRAPH_X_START, y_pos)
            cr.set_line_width (0.3 if value == 0 else 0.07)
            cr.line_to(GRAPH_X_START + GRAPH_WIDTH, y_pos)
        else:
            # Left Y scale
            if value != VALUE_MAX and value != VALUE_MIN:
                cr.move_to(x_pos - 3, y_pos)
                cr.line_to(x_pos + 3, y_pos)
            # Right Y scale
            cr.move_to(GRAPH_X_START + GRAPH_WIDTH, y_pos)
            cr.line_to(GRAPH_X_START + GRAPH_WIDTH - 3, y_pos)
        y_pos += (GRAPH_HEIGHT / float(VALUE_SPACE))
        value -= VALUE_STEP
        cr.stroke()

    # Draw seconds
    cr.set_source_rgb(0x00, 0x00, 0x00)
    cr.select_font_face('Roboto', cairo.FONT_SLANT_NORMAL)
    cr.set_font_size(12)

    for second in SECONDS:
        if second['pos'] >= GRAPH_X_START:
            cr.set_source_rgb(0x00, 0x00, 0x00)
            cr.set_line_width(0.5)
            if second['value'] % 5 == 0:
                # Bottom scale
                ext = cr.text_extents(str(second['value']))
                cr.move_to(second['pos'] - ext[2] / 2, GRAPH_Y_START + GRAPH_HEIGHT + ext[3] + 10)
                cr.show_text(str(second['value']))
                cr.move_to(second['pos'], GRAPH_Y_START + GRAPH_HEIGHT - 6)
                cr.line_to(second['pos'], GRAPH_Y_START + GRAPH_HEIGHT + 6)
                # Top scale
                cr.move_to(second['pos'], GRAPH_Y_START)
                cr.line_to(second['pos'], GRAPH_Y_START + 6)
            else:
                # Bottom scale
                cr.move_to(second['pos'], GRAPH_Y_START + GRAPH_HEIGHT - 3)
                cr.line_to(second['pos'], GRAPH_Y_START + GRAPH_HEIGHT + 3)
                # Top scale
                cr.move_to(second['pos'], GRAPH_Y_START)
                cr.line_to(second['pos'], GRAPH_Y_START + 3)
            cr.stroke()

    # Green green rectangle (0 - 500)
    if len(SECONDS) > 0:
        cr.set_line_width(0)
        cr.set_source_rgba(0x00, 0xff, 0x00, 0.15) # With alpha channel
        if SECONDS[0]['value'] == 0 and SECONDS[0]['pos'] >= GRAPH_X_START:
            x_pos = SECONDS[0]['pos']
        else:
            x_pos = GRAPH_X_START
        if SECONDS[0]['value'] == 0:
            width = GRAPH_X_START + GRAPH_WIDTH - SECONDS[0]['pos']
        else:
            width = GRAPH_WIDTH
        cr.rectangle(x_pos, value_pos(500), width, value_pos(0) - value_pos(500))
        cr.fill()
        cr.stroke()

    # Draw curve
    #if DEVICE_ENABLED is False:
    #    curve = {'pos': GRAPH_X_START + GRAPH_WIDTH, 'value': random.Random().randint(-50, 100)}
    #    CURVES.append(curve)
    #    if len(CURVES) > CURVE_MAX:
    #        CURVES.pop(0)

    cr.set_line_width(1.75)
    cr.set_source_rgba(0x00, 0x00, 0xff)
    length = len(CURVES)
    for i in range(0, length):
        if i != 0 and CURVES[i]['pos'] >= GRAPH_X_START:
            prev_y_pos = value_pos(CURVES[i - 1]['value'])
            curr_y_pos = value_pos(CURVES[i]['value'])
            cr.move_to(CURVES[i - 1]['pos'], prev_y_pos)
            cr.line_to(CURVES[i]['pos'], curr_y_pos)
    cr.stroke()

    # Draw bottom 'TIME (S)' test
    cr.set_source_rgb(0x00, 0x00, 0x00)
    cr.select_font_face('Roboto', cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    cr.set_font_size(12)
    text = 'TIME (S)'
    ext = cr.text_extents(text)
    cr.move_to(GRAPH_X_START + GRAPH_WIDTH / 2 - ext[2] / 2, GRAPH_Y_START + GRAPH_HEIGHT + 35)
    cr.show_text(text)
    cr.stroke()

    return False

def delete_event_cb(window, *args):
    Gtk.main_quit()
    return False

def button_press_event_cb(widget, event, drawing):
    if event.type == Gdk.EventType._3BUTTON_PRESS and event.button == 1:
        start_thread(drawing, True)
    return False

def key_press_event_cb(widget, event, drawing):
    global KEY_IS_PRESSED

    if KEY_IS_PRESSED is True:
        return False

    KEY_IS_PRESSED = True    
    if event.keyval == Gdk.KEY_space:
        start_thread(drawing, True)
    return False

def key_release_event_cb(widget, event):
    global KEY_IS_PRESSED

    KEY_IS_PRESSED = False
    return False

def touch_event_cb(widget, event, drawing):
    global TOUCH_BEGIN
    global TOUCH_TIME

    coords = event.get_coords()
    if coords[0] is True and coords[1] <= GRAPH_X_START and coords[2] <= GRAPH_X_START:
        if event.type == Gdk.EventType.TOUCH_BEGIN:
            if TOUCH_BEGIN is False:
                TOUCH_BEGIN = True
                TOUCH_TIME = GLib.get_monotonic_time()

        if event.type == Gdk.EventType.TOUCH_UPDATE:
            if TOUCH_BEGIN is True:
                if GLib.get_monotonic_time() - TOUCH_TIME >= 1000000:
                    start_thread(drawing, True)
                    TOUCH_BEGIN = False

    if event.type == Gdk.EventType.TOUCH_END:
        TOUCH_BEGIN = False
    return False

def inc_sec(drawing):
    global ELAPSED_TIME
    ELAPSED_TIME += INTERVAL
    drawing.queue_draw()
    return True

def queue_draw(drawing):
    drawing.queue_draw()
    return False

def read_device(drawing):
    global ELAPSED_TIME
    global DEVICE_ENABLED
    global THREAD_IS_RUN

    if DEVICE_ENABLED is False:
        return

    try:
        bus = smbus.SMBus(DEV_BUS)
    except IOError as e:
        print e.message
        return

    while THREAD_IS_RUN:
        try:
            # SingleTac manual section 2.4.3 I2C Read Operation:
            # Where a Read operation is not preceded by a Read Request operation the read location defaults to
            # 128 (the sensor output location) and consecutive reads will therefore simply read the default 32 bytes
            # of the sensor data region.
            # Here we read only 6 bytes from 128 to 133
            data = bus.read_i2c_block_data(DEV_ADDRESS, 0x00, 6)

            frameindex = data[0] << 8 | data[1]
            timestamp = data[2] << 8 | data[3]
            value = (data[4] << 8 | data[5]) - 255

            if OPT_VERBOSE:
                args = (frameindex, timestamp, value, ELAPSED_TIME / float(1000))
                sys.stderr.write('frameindex=%i timestamp=%i value=%i sec=%.2f\n' % args)

        except IOError as e:
            if len(CURVES) > 0:
                value = CURVES[-1]['value']
            else:
                value = 0

            if OPT_VERBOSE:
                sys.stderr.write('%s sec=%.2f\n' % (str(e), ELAPSED_TIME / float(1000)))

        # Use previous value for "incorrect" data
        if frameindex == 0xffff and timestamp == 0xffff:
            if len(CURVES) > 0:
                value = CURVES[-1]['value']
            else:
                value = 0

        # Invalid frame index which is less than previous index
        if len(CURVES) > 0:
            if frameindex < CURVES[-1]['frameindex'] and CURVES[-1]['frameindex'] != 0xffff:
                value = CURVES[-1]['value']
                frameindex = CURVES[-1]['frameindex'] + 1

        # Normalize value if it exceeds the VALUE_MAX or VALUE_MIN
        # This will prevent drawing outside the graph
        if value > VALUE_MAX:
            value = VALUE_MAX
        if value < VALUE_MIN:
            value = VALUE_MIN

        # Append curves
        curve = {'value': value, 'frameindex': frameindex, 'pos': GRAPH_X_START + GRAPH_WIDTH}
        CURVES.append(curve)
        if len(CURVES) > CURVE_MAX:
            CURVES.pop(0)

        # Apply dynamic position
        for curve in CURVES:
            curve['pos'] -= (SECOND_SPACE * INTERVAL / 1000)

        # Append seconds
        if ELAPSED_TIME % 1000 == 0:
            second = {'pos': GRAPH_X_START + GRAPH_WIDTH, 'value': ELAPSED_TIME / 1000}
            if len(SECONDS) > SECOND_MAX:
                SECONDS.pop(0)
            SECONDS.append(second)

        # Apply dynamic position
        for second in SECONDS:
            second['pos'] -= (SECOND_SPACE * INTERVAL / 1000)

        # Emit drawing
        GLib.idle_add(queue_draw, drawing)
        time.sleep(INTERVAL / float(1000))
        ELAPSED_TIME += INTERVAL

def start_thread(drawing, restart=False):
    global READ_THREAD
    global THREAD_IS_RUN
    global ELAPSED_TIME
    global SECONDS
    global CURVES

    if restart is True:
        THREAD_IS_RUN = False
        READ_THREAD.join()
    ELAPSED_TIME = 0
    SECONDS = []
    CURVES = []
    THREAD_IS_RUN = True
    READ_THREAD = threading.Thread(target=read_device, args=(drawing,))
    READ_THREAD.start()

def stop_thread():
    global THREAD_IS_RUN
    global READ_THREAD

    THREAD_IS_RUN = False
    READ_THREAD.join()

if __name__ == '__main__':
    window = Gtk.Window()
    window.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
    window.set_default_size(WINDOW_WIDTH, WINDOW_HEIGHT)
    window.set_title('PPS SingleTact Demo')
    window.maximize()
    window.connect('delete-event', Gtk.main_quit)

    drawing = Gtk.DrawingArea()
    drawing.connect('draw', drawing_draw_cb)

    window.add(drawing)
    window.connect('button-press-event', button_press_event_cb, drawing)
    window.connect('key-press-event', key_press_event_cb, drawing)
    window.connect('key-release-event', key_release_event_cb)
    window.connect('touch-event', touch_event_cb, drawing)
    window.show_all()

    start_thread(drawing)

    Gtk.main()

    stop_thread()

    sys.exit(0)
