try:
    import msvcrt
except ImportError:
    USE_WINDOWS = False
    import sys
    import select
    import tty
    import termios
    class KeyboardHandler(object):
        def __enter__(self):
            self.old_settings = termios.tcgetattr(sys.stdin)
            tty.setcbreak(sys.stdin.fileno())
            return self
        def __exit__(self, tp, value, traceback):
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old_settings)
        def get_data(self):
            if select.select([sys.stdin], [], [], 0) == ([sys.stdin],[],[]):
                return sys.stdin.read(1)
            return '\xff'
else:
    USE_WINDOWS = True
    class KeyboardHandler(object):
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass
        def get_data(self):
            if msvcrt.kbhit():
                ch = msvcrt.getche()
                return ch
            return '\xff'

if __name__=='__main__':
    from time import sleep
    with KeyboardHandler() as k:
        sleep(5)
        print (k.get_data())
