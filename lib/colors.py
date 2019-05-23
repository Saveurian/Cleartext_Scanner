class Colors:
    """
    Provides ANSI terminal colors helping the eyes identify
    potential clear-text passwords.
    """
    NONE = "\033[0m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    LIGHT_GRAY = "\033[37m"
    LIGHT_BLUE = "\033[34m"
    YELLOW = "\033[33m"

    def __init__(self):
        return

    # Red terminal color
    def red(self, text):
        return self.RED + text + self.NONE

    # Green terminal color
    def green(self, text):
        return self.GREEN + text + self.NONE

    # Light gray terminal color
    def light_gray(self, text):
        return self.LIGHT_GRAY + text + self.NONE

    # Light blue terminal color
    def light_blue(self, text):
        return self.LIGHT_BLUE + text + self.NONE

    # Yellow terminal color
    def yellow(self, text):
        return self.YELLOW + text + self.NONE
