import os
import time
import random
import signal
import sys
import re
import hashlib
from colors import Colors


class Scanner:
    def __init__(self, project='Untitled', source='.', ignored_paths=None, color=False,
                 filter_obj=None, verbose=False, outfile=None, quiet=False):
        """
        Constructor.
        :type project: str
        :param project: str
        :param ignored_paths: bool
        :param source: str
        :param color: bool
        :param filter_obj: lib.Filter()
        :param verbose: bool
        :param outfile: str
        :param quiet: bool
        """
        self.project = project
        self.source = source
        self.color = False
        if color:
            self.color = Colors()
        self.filter = filter_obj
        self.verbose = verbose
        self.outfile = outfile
        self.fp = None
        self.html = ''
        self.quiet = quiet
        if ignored_paths:
            paths = ignored_paths.split(':')
            for path in paths:
                self.filter.ignored_paths.append(re.compile(path, self.filter.REGEX_FLAGS))
        self.html = open('resources/output_template.html', 'r').read()
        self.fp = open(self.outfile, 'w')
        self.html = self.html.replace('###DIRECTORY###', self.source)
        self.html = self.html.replace('###PROJECT###', self.project)

    def scan(self):
        """
        Crawls all eligible files in a folder and scans each line of
        eligible files for potential clear-text passwords.
        """

        def signal_handler(sig, frame):
            """
            Handles Ctrl+C being pressed (SIGINT)
            :param sig: Unused
            :param frame: Unused
            :return: void
            """
            self.cleanup(interrupted=True)

        signal.signal(signal.SIGINT, signal_handler)

        """
        Start walking the directories...
        """
        for root, sub_folders, files in os.walk(self.source):
            for filename in files:
                full_path = os.path.join(root, filename)
                if not self.filter.is_ignored_file(filename) and not self.filter.is_ignored_file(root):

                    """
                    Skip files beginning with a period.
                    If there is no file extension, use file name.
                    """
                    if re.match(r"^\.", filename):
                        continue

                    try:
                        garbage, extension = os.path.splitext(full_path)
                        try:
                            extension = extension.split('.')[1]
                        except IndexError:
                            pass

                        try:
                            pattern = self.filter.patterns_by_filetype[extension]
                        except KeyError:
                            """ Key not found in lookup table in filter.py """
                            continue

                        if pattern:
                            if not self.quiet:
                                if self.verbose:
                                    sys.stdout.write("\nScanning {0}".format(full_path))
                                    sys.stdout.flush()
                                else:
                                    sys.stdout.write('.')
                                    sys.stdout.flush()

                            line_number = 0
                            random.seed(time.time())

                            filep = open(full_path, 'r')

                            if filep.read(3) == '/*!':
                                """
                                Ignore vendor JavaScript files
                                which commonly begin with '/*!' to tell YUI compressor
                                not to remove their header comment.
                                """
                                continue

                            for line in filep:
                                rnum = random.randint(1, 1000000)
                                line_number += 1
                                if self.filter.is_ignored_pattern(line):
                                    continue

                                def search_in_line(_pattern, _line):
                                    match = _pattern.search(_line)
                                    if match:
                                        _line = _line.strip()

                                        if re.match('<|>', _line, re.MULTILINE):
                                            _line = re.sub('<', '&lt;', _line, re.MULTILINE)
                                            _line = re.sub('>', '&gt;', _line, re.MULTILINE)

                                        try:
                                            password = match.group(2).strip()
                                        except IndexError:
                                            password = match.group(1).strip()
                                            if not password:
                                                password = match.group(0).strip()

                                        if password:
                                            if not self.quiet:
                                                if self.color:
                                                    print "\n{0}:{1}: {2}".format(
                                                        self.color.light_gray(full_path),
                                                        self.color.light_blue(str(line_number)),
                                                        _line.replace(password, self.color.red(password)
                                                    ))
                                                else:
                                                    print "\n{0}:{1}: {2}".format(full_path, str(line_number), _line)

                                            """ Output to HTML file """
                                            highlight = _line.replace(password,
                                                                     '<span class="highlight">{0}</span>'.format(password))
                                            self.html = self.html.replace(
                                                '###OUTPUT###',
                                                '<tr>'
                                                '<td>{0}:<span class="line-number">{1}</span></td><td><b>{2}</b>'
                                                '<span class="expand" id="expand-{3}">[+]</span>'
                                                '<div class="hidden" id="hidden-{4}"><code>{5}</code></div></td>'
                                                '</tr>###OUTPUT###'.format(
                                                full_path,
                                                str(line_number),
                                                password,
                                                str(rnum),
                                                str(rnum),
                                                highlight
                                            ))

                                if type(pattern) is list:
                                    for p in pattern:
                                        search_in_line(p, line)
                                else:
                                    search_in_line(pattern, line)
                            filep.close()
                        else:
                            """ File doesn't match filter criteria """
                            continue
                    except Exception, e:
                        print full_path
                        print '{0}: {1}'.format(str(e.__class__), str(e))
                        raise
        self.cleanup()

    def results_haved_changed(self):
        """
        Compare SHA256 hash of collected output against the
        hash of the previous output file.
        :return: boolean
        """
        self.html = self.html.replace('###OUTPUT###', '')
        hash1 = hashlib.sha256(self.html).hexdigest()
        try:
            previous_results = open(self.outfile, 'r').read()
            hash2 = hashlib.sha256(previous_results).hexdigest()
            if hash1 != hash2:
                return False
            return True
        except IOError:
            return False

    def cleanup(self, interrupted=False):
        """
        Cleans up and closes out the output file if one was specified.
        :param interrupted: bool
        :return: void
        """
        if interrupted:
            print "\nUser cancelled. Cleaning up..."
        if self.fp:
            self.html = self.html.replace('###OUTPUT###', '')
            self.fp.truncate(0)
            self.fp.write(self.html)
            self.fp.close()
        if interrupted:
            sys.exit(1)
