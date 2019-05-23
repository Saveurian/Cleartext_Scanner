import re
import os


class Filter:
    """
    Provides filter patterns and utility methods for PasswordScanner.
    Attributes:
        patterns_by_filetype        dict of supported file types and their associated regex.
        ignored_paths               list of regexes of paths to ignore.
        ignored_filename_patterns   list of regexes of file name patterns to ignore.
        ignored_patterns            list of regexes of patterns to ignore on each line of a file.
    Usage:
    >>> from lib.filter import Filter
    >>> from lib.scanner import Scanner
    >>> f = Filter()
    >>> s = Scanner(filter_obj=f, ...)
    """
    REGEX_FLAGS = re.IGNORECASE | re.UNICODE | re.LOCALE
    CATCH_ALL = re.compile("(pwd.*|salt.*|.*secret.*|passw.*)", REGEX_FLAGS)
    C_STYLE = re.compile("(pwd.*|salt.*|.*secret.*|passw.*)\s*=\s*['\"](.*?)['\"]", REGEX_FLAGS)
    CFG_STYLE = re.compile("(?!.*ENC\(.*\))(pwd.*|salt.*|.*secret.*|passw.*)['|\"]*(.*?)['|\"]*", REGEX_FLAGS)
    CONF_STYLE = re.compile("(pwd.*|salt.*|.*secret.*|passw.*)\W+\W*\s*[\"|'](.*?)['|\"]\s*", REGEX_FLAGS)
    CONFIG_STYLE = re.compile("(pwd.*|Password)\s*=\s*(.*?);", REGEX_FLAGS)
    ASM_STYLE = re.compile("(pwd.*|salt.*|secret.*|passw.*):*\s+db\s*['\"]+(.*)['\"]", REGEX_FLAGS)
    FTP_CONNECTION_STRING = re.compile('://(\w+)+:([a-zA-Z0-9\$#!]+)@', REGEX_FLAGS)

    patterns_by_filetype = {
        'Rakefile': C_STYLE,
        'Makefile': C_STYLE,
        'php': C_STYLE,
        'ini': C_STYLE,
        'cgi': C_STYLE,
        'rb': C_STYLE,
        'inc': C_STYLE,
        'properties': CFG_STYLE,
        'java': C_STYLE,
        'tea': C_STYLE,
        'c': C_STYLE,
        'cc': C_STYLE,
        'cpp': C_STYLE,
        'm': C_STYLE,
        'h': C_STYLE,
        'js': C_STYLE,
        'json': C_STYLE,
        'txt': C_STYLE,
        'html': CATCH_ALL,
        'htm': CATCH_ALL,
        'phtml': C_STYLE,
        'xml': CATCH_ALL,
        'sh': CATCH_ALL,
        'erb': CATCH_ALL,
        'bat': CATCH_ALL,
        'sql': CATCH_ALL,
        'conf': CONF_STYLE,
        'config': CONFIG_STYLE,
        'cfg': [CFG_STYLE, FTP_CONNECTION_STRING],
        'py': C_STYLE,
        's': ASM_STYLE,
        'asm': ASM_STYLE,
        'asp': CATCH_ALL,
        'as': C_STYLE,
        'jsp': C_STYLE,
        'aspx': CATCH_ALL,
        'mustache': CATCH_ALL,
        'groovy': C_STYLE,
        'coffee': C_STYLE,
        'tpl': C_STYLE,
        'cs': C_STYLE,
        'vb': C_STYLE,
        'ashx': CATCH_ALL,
        'default': CATCH_ALL
    }

    """ Paths to ignore. Can be partial path or path to file. """
    ignored_paths = [
        re.compile('.*target.*', REGEX_FLAGS),
        re.compile('.*build.*', REGEX_FLAGS),
        re.compile('.*tests.*', REGEX_FLAGS),
        re.compile('\.git', REGEX_FLAGS),
        re.compile('\.doc', REGEX_FLAGS),
        re.compile('\.idea', REGEX_FLAGS),
        re.compile('\.svn', REGEX_FLAGS),
        re.compile('\.workspace', REGEX_FLAGS)
    ]

    """ Filename patterns to ignore """
    ignored_filename_patterns = (
        re.compile('mootools-\d\.\d\.\d.*\.js', REGEX_FLAGS),
        re.compile('jquery-\d\.\d\.\d.*\.js', REGEX_FLAGS),
        re.compile('jquery-\d+\.\d+\.\d+\.min\.js', REGEX_FLAGS),
        re.compile('jquery-ui-\d\.\d\.\d.*\.js$', REGEX_FLAGS),
        re.compile('less-\d\.\d\.\d.*\.js$', REGEX_FLAGS),
        re.compile('jquery\.cycle.*js$', REGEX_FLAGS),
        re.compile('angular.*\.js', REGEX_FLAGS),
        re.compile('modernizr.*\.js', REGEX_FLAGS),
        re.compile('swagger-ui.*.js', REGEX_FLAGS),
        re.compile('underscore.*.js', REGEX_FLAGS),
        re.compile('.*Test.*', REGEX_FLAGS)
    )

    """
    Patterns to ignore within files.
    For example, constants with names like PASSWORD_FORM_FIELD_ID will
    trigger false positives.
    """
    ignored_patterns = (
        re.compile('.*form.*', REGEX_FLAGS),
        re.compile('.*forgot.*', REGEX_FLAGS),
        re.compile('.*label.*', REGEX_FLAGS),
        re.compile('.*class.*', REGEX_FLAGS),
        re.compile('.*change.*', REGEX_FLAGS),
        re.compile('.*<input.*', REGEX_FLAGS)
    )

    def __init__(self):
        return

    def is_ignored_file(self, name):
        """
        Returns True or False if the filename is to be ignored.
        This is based on conditions defined throughout the rest of this file.
        :param name: Filename string
        :return: bool
        """
        try: # If the file extension is not in patterns_by_filetype, return True.
            ext = os.path.splitext(name)[1].split('.')[1]
            if ext not in self.patterns_by_filetype:
                return True
        except IndexError:
            pass
        if any(pattern.search(name) for pattern in self.ignored_paths):
            return True
        if any(pattern.search(name) for pattern in self.ignored_filename_patterns):
            return True
        if os.path.basename(name).startswith('.'):
            # Ignore hidden files
            return True
        return False

    def is_ignored_pattern(self, line):
        """
        Returns true if the string passed contains a pattern to ignore. False otherwise.
        :param line: Line-text string
        :return: bool
        """
        return any(pattern.search(line) for pattern in self.ignored_patterns)
