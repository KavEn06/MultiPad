# You import all the IOs of your board
import board
import busio
import adafruit_ssd1306

# These are imports from the kmk library
from kmk.kmk_keyboard import KMKKeyboard
from kmk.scanners.keypad import KeysScanner
from kmk.keys import KC
from kmk.modules.layers import Layers
from kmk.modules.macros import Press, Release, Tap, Macros, Delay
from kmk.modules.encoder import EncoderHandler

# This is the main instance of your keyboard
keyboard = KMKKeyboard()
i2c = busio.I2C(board.SCL, board.SDA)

# global audio variable 
is_headphones = True 

# Add the macro extension
macros = Macros()
layers = Layers()
keyboard.modules.append(macros)
keyboard.modules.append(layers)
display = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)

# rotary encoder
class LayerScrollEncoder(EncoderHandler):
    def __init__(self):
        super().__init__()
        self.layer_scroll_mode = False
        self.selected_layer = 0
        self.max_layer = len(keyboard.keymap) - 1
        self.keymap_names = ["General", "VS Code", "OnShape", "Gaming"]
        
        display.fill(0)
        display.text(self.keymap_names[self.selected_layer], 0, 0, 1)
        display.show()

    def on_encoder_button(self, index, is_pressed):
        if is_pressed:
            self.layer_scroll_mode = True
            self.selected_layer = keyboard.active_layer
        else:
            self.layer_scroll_mode = False
            keyboard.active_layer = self.selected_layer

            display.fill(0)
            display.text(self.keymap_names[self.selected_layer], 0, 0, 1)
            display.show()

        return True  # Tell KMK we handled this


    def on_encoder_turn(self, encoder_index, clockwise):
        if self.layer_scroll_mode:
            # Scroll through layers while encoder button is held
            if clockwise:
                self.selected_layer = (self.selected_layer + 1) % (self.max_layer + 1)

                display.fill(0)
                display.text(self.keymap_names[self.selected_layer], 0, 0, 1)
                display.show()
            else:
                self.selected_layer = (self.selected_layer - 1) % (self.max_layer + 1)

                display.fill(0)
                display.text(self.keymap_names[self.selected_layer], 0, 0, 1)
                display.show()

            print(f"[Layer Scroll] Selected layer: {self.selected_layer}")
            return True  # Block default encoder behavior

        if keyboard.active_layer == 2:
            # CAD layer: Zoom in/out
            zoom_key = KC.LCTL(KC.EQL) if clockwise else KC.LCTL(KC.MINS)
            keyboard.tap_key(zoom_key)
            return True

        # Volume control
        volume_key = KC.VOLU if clockwise else KC.VOLD
        keyboard.tap_key(volume_key)
        return True

# output audio switcher 
def toggle_audio_output():
    global is_headphones
    
    sequence = [
        Tap(KC.LGUI(KC.B)),     Delay(150),  
        Tap(KC.RIGHT),          Delay(150),
        Tap(KC.ENTER),          Delay(250),
        Tap(KC.TAB),            Delay(150),
        Tap(KC.ENTER),          Delay(250),
    ]

    if is_headphones:
        sequence.append(Tap(KC.UP))   # Go to monitor
        is_headphones = False

    else:
        sequence.append(Tap(KC.DOWN)) # Go to headphones
        is_headphones = True

    sequence.append(Delay(200))
    sequence.append(Tap(KC.ENTER))  

    return KC.MACRO(*sequence)

#macros
open_gmail = KC.MACRO(
    Tap(KC.LCTL(KC.T)),
    Tap(KC.G), Tap(KC.M), Tap(KC.A), Tap(KC.I), Tap(KC.L),
    Tap(KC.DOT),
    Tap(KC.C), Tap(KC.O), Tap(KC.M),
    Tap(KC.ENTER)
)

git_clone = KC.MACRO(
    Tap(KC.LCTL(KC.LSFT(KC.P))),  

    Tap(KC.G), Tap(KC.I), Tap(KC.T), Tap(KC.COLON), Tap(KC.SPACE),
    Tap(KC.C), Tap(KC.L), Tap(KC.O), Tap(KC.N), Tap(KC.E),

    Tap(KC.ENTER),               
    Tap(KC.LCTL(KC.V)),           
    Tap(KC.ENTER)               
)

discord_mute = KC.MACRO(
    Tap(KC.LGUI(KC._1)),           
    Tap(KC.LCTL(KC.LSFT(KC.M))),
    Tap(KC.LALT(KC.TAB))            
)

discord_deafen = KC.MACRO(
    Tap(KC.LGUI(KC._1)),        
    Tap(KC.LCTL(KC.LSFT(KC.D))),  
    Tap(KC.LALT(KC.TAB))        
)

toggle_output = toggle_audio_output

# Define your pins here!
PINS = [
    board.GP29, board.GP0, board.GP1,
    board.GP28, board.GP27, board.GP26,
]

# Tell kmk we are not using a key matrix
keyboard.matrix = KeysScanner(
    pins=PINS,
    value_when_pressed=False,
)

# Here you define the buttons corresponding to the pins
# Look here for keycodes: https://github.com/KMKfw/kmk_firmware/blob/main/docs/en/keycodes.md
# And here for macros: https://github.com/KMKfw/kmk_firmware/blob/main/docs/en/macros.md
keyboard.keymap = [
    [
        toggle_output,          discord_mute,               KC.LGUI(KC.LSFT(KC.S)),
        KC.MEDIA_PREV_TRACK,    KC.MEDIA_NEXT_TRACK,        KC.MEDIA_PLAY_PAUSE,
    ],

    [
        KC.LCTL(KC.F5),         git_clone,                  KC.LSFT(KC.LALT(KC.DOWN)),
        KC.LCTL(KC.Z),          KC.LCTL(KC.SLSH),           KC.MEDIA_PLAY_PAUSE,
    ], 

    [
        KC.LSFT(KC._7),         KC.LSFT(KC.S),              KC.LSFT(KC.E),
        KC.LSFT(KC.X),          KC.LBRC,                    KC.MEDIA_PLAY_PAUSE,
    ],
    
    [
        toggle_output,          discord_mute,               discord_deafen,
        KC.NO,                  KC.NO,                      KC.NO,
    ]
]

encoder_handler = LayerScrollEncoder()
keyboard.modules.append(encoder_handler)
encoder_handler.pins = ((board.GP4, board.GP2, board.GP3, False),)

# Start kmk!
if __name__ == '__main__':
    keyboard.go()