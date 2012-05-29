"""
The controls module maps the player's keyboard keys to their controls.

classes:
  Quit                          An Exception that is raised when the player quits
                                the game.

functions:
  quit                          Quit the game.
  flip_pause_state              Pause/unpause the game.
  reset_player                  Move the player back to starting position, and
                                reset the player's velocity.

              JSON __doc__

         Keyboard Key Configuration

Supported Keys
In the JSON database, map each entry in the KeyBinding column of Supported Key
Bindings to a list of keys in the KeyASCII column of Supported Keys.

           Supported Key Bindings
=============================================
      KeyBinding    Description
      ==========    ===========
      quit          Quits the game.
      pause         Pause/Unpauses the game.
      reset         Resets the position of
                    the player.
      jetpack_up    Enables your jetpack
                    upward.
      jetpack_left
                    Enables your jetpack
                    leftward.
      jetpack_right
                    Enables your jetpack
                    rightward.



               Supported Keys
(taken from http://www.pygame.org/docs/ref/key.html)
==============================================
      KeyASCII      ASCII   Common Name
      ========      =====   ===========
      K_BACKSPACE    \b      backspace
      K_TAB          \t      tab
      K_CLEAR                clear
      K_RETURN       \r      return
      K_PAUSE                pause
      K_ESCAPE       ^[      escape
      K_SPACE                space
      K_EXCLAIM      !       exclaim
      K_QUOTEDBL     "       quotedbl
      K_HASH         #       hash
      K_DOLLAR       $       dollar
      K_AMPERSAND    &       ampersand
      K_QUOTE                quote
      K_LEFTPAREN    (       left parenthesis
      K_RIGHTPAREN   )       right parenthesis
      K_ASTERISK     *       asterisk
      K_PLUS         +       plus sign
      K_COMMA        ,       comma
      K_MINUS        -       minus sign
      K_PERIOD       .       period
      K_SLASH        /       forward slash
      K_0            0       0
      K_1            1       1
      K_2            2       2
      K_3            3       3
      K_4            4       4
      K_5            5       5
      K_6            6       6
      K_7            7       7
      K_8            8       8
      K_9            9       9
      K_COLON        :       colon
      K_SEMICOLON    ;       semicolon
      K_LESS         <       less-than sign
      K_EQUALS       =       equals sign
      K_GREATER      >       greater-than sign
      K_QUESTION     ?       question mark
      K_AT           @       at
      K_LEFTBRACKET  [       left bracket
      K_BACKSLASH    \       backslash
      K_RIGHTBRACKET ]      right bracket
      K_CARET        ^       caret
      K_UNDERSCORE   _       underscore
      K_BACKQUOTE    `       grave
      K_a            a       a
      K_b            b       b
      K_c            c       c
      K_d            d       d
      K_e            e       e
      K_f            f       f
      K_g            g       g
      K_h            h       h
      K_i            i       i
      K_j            j       j
      K_k            k       k
      K_l            l       l
      K_m            m       m
      K_n            n       n
      K_o            o       o
      K_p            p       p
      K_q            q       q
      K_r            r       r
      K_s            s       s
      K_t            t       t
      K_u            u       u
      K_v            v       v
      K_w            w       w
      K_x            x       x
      K_y            y       y
      K_z            z       z
      K_DELETE               delete
      K_KP0                  keypad 0
      K_KP1                  keypad 1
      K_KP2                  keypad 2
      K_KP3                  keypad 3
      K_KP4                  keypad 4
      K_KP5                  keypad 5
      K_KP6                  keypad 6
      K_KP7                  keypad 7
      K_KP8                  keypad 8
      K_KP9                  keypad 9
      K_KP_PERIOD    .       keypad period
      K_KP_DIVIDE    /       keypad divide
      K_KP_MULTIPLY  *       keypad multiply
      K_KP_MINUS     -       keypad minus
      K_KP_PLUS      +       keypad plus
      K_KP_ENTER     \r      keypad enter
      K_KP_EQUALS    =       keypad equals
      K_UP                   up arrow
      K_DOWN                 down arrow
      K_RIGHT                right arrow
      K_LEFT                 left arrow
      K_INSERT               insert
      K_HOME                 home
      K_END                  end
      K_PAGEUP               page up
      K_PAGEDOWN             page down
      K_F1                   F1
      K_F2                   F2
      K_F3                   F3
      K_F4                   F4
      K_F5                   F5
      K_F6                   F6
      K_F7                   F7
      K_F8                   F8
      K_F9                   F9
      K_F10                  F10
      K_F11                  F11
      K_F12                  F12
      K_F13                  F13
      K_F14                  F14
      K_F15                  F15
      K_NUMLOCK              numlock
      K_CAPSLOCK             capslock
      K_SCROLLOCK            scrollock
      K_RSHIFT               right shift
      K_LSHIFT               left shift
      K_RCTRL                right ctrl
      K_LCTRL                left ctrl
      K_RALT                 right alt
      K_LALT                 left alt
      K_RMETA                right meta
      K_LMETA                left meta
      K_LSUPER               left windows key
      K_RSUPER               right windows key
      K_MODE                 mode shift
      K_HELP                 help
      K_PRINT                print screen
      K_SYSREQ               sysrq
      K_BREAK                break
      K_MENU                 menu
      K_POWER                power
      K_EURO                 euro

"""

import json
import os

import pygame

import event
import physics

provider = None

class Quit(Exception):
    """An Exception that is raised when the player quits."""
    pass

class InvalidKeyError(Exception):
    """Raised when there is an invalid key mapping in the keyboard.json config."""
    pass

# Control functions

def quit():
    """Quit the game."""
    raise Quit
    return [], []

def flip_pause_state():
    """Pause/unpause the game."""
    provider.pause()
    return [], []

def reset_player():
    """
    Move the player back to starting position, and reset the player's velocity.

    """
    provider.current_level.player.position = provider.current_level._PlayerPosition
    provider.current_level.player.velocity = provider.current_level._PlayerVelocity
    provider.current_level.player.invalidate_intersections()
    ints = physics.find_intersections(provider, provider.current_level.player)
    provider.current_level.player.intersections.extend(ints)

    return ints, []

    provider.current_level.reset_player()


def init(provider_):
    global provider
    provider = provider_
    # map control names to their functions
    control_to_keypress_control = {
        "quit": quit,
        "pause": flip_pause_state,
        "reset": reset_player
    }

    control_to_keytoggle_control = {
        "jetpack_up": provider.current_level.player._jetpack_up,
        "jetpack_left": provider.current_level.player._jetpack_left,
        "jetpack_right": provider.current_level.player._jetpack_right
    }

    # open cfg/keyboards.json, and load in user's control mapping
    config_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "../cfg")

    with open(os.path.join(config_path, "keyboard.json")) as config:
        control_to_keys = json.load(config)


    # decode controls and associate keyboard keys with the controls
    for control in control_to_keys:
        if control in control_to_keypress_control:
            for key in control_to_keys[control]:
                if not key.startswith("K_"):
                    # pygame keys all start with "K_"
                    raise InvalidKeyError("Invalid key " + key + " mapped from control " + control + " in cfg/keyboard.json")
                try:
                    pygame_key = getattr(pygame, key)
                except AttributeError:
                    raise InvalidKeyError("Invalid key " + key + " mapped from control " + control + " in cfg/keyboard.json")
                event.KeyPressRealEvent[pygame_key].register(control_to_keypress_control[control])
        elif control in control_to_keytoggle_control:
            for key in control_to_keys[control]:
                if not key.startswith("K_"):
                    # pygame keys all start with "K_"
                    raise InvalidKeyError("Invalid key " + key + " mapped from control " + control + " in cfg/keyboard.json")
                try:
                    pygame_key = getattr(pygame, key)
                except AttributeError:
                    raise InvalidKeyError("Invalid key " + key + " mapped from control " + control + " in cfg/keyboard.json")
                event.KeyToggleRealEvent[pygame_key].register(control_to_keytoggle_control[control])
