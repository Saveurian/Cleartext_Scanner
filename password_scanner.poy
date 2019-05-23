"""
 Recursively scan current folder potential clear-text passwords
 and generate an HTML report.
"""

import argparse
import sys
import time
from lib.filter import Filter
from lib.scanner import Scanner


# Process command line arguments
parser = argparse.ArgumentParser(description='Scan and report on a project for potential clear-text passwords.')
parser.add_argument('-q', '--quiet', help='Do not list potential passwords.',
                    default=False, dest='quiet', action='store_true')
parser.add_argument('-c', '--color',   help='Use ANSI terminal colors during output.',
                    dest='color', default=False, action='store_true')
parser.add_argument('-v', '--verbose', help='Output more information.', default=False, dest='verbose',
                    action='store_true')
parser.add_argument('-p', '--project', help='Project name.', dest='project', required=True)
parser.add_argument('-s', '--source',  help='Path to project source code.', default='.', dest='source', required=True)
parser.add_argument('-o', '--outfile', help='Name of output file (HTML).', dest='outfile', default='', required=False)
parser.add_argument('-i', '--ignored-paths',
                    help='A colon separated list of keywords for paths to ignore during the scan.',
                    default=None, required=False)
args = parser.parse_args()


def main():
    """
    Create a filter object, a scanner object, and do all the cool stuff...
    """
    f = Filter()

    if not args.outfile:
        args.outfile = '{0}-{1}.html'.format(args.project, time.strftime('%Y-%m-%d'))

    scanner = Scanner(project=args.project,
                      source=args.source,
                      ignored_paths=args.ignored_paths,
                      color=args.color,
                      filter_obj=f,
                      verbose=args.verbose,
                      outfile=args.outfile,
                      quiet=args.quiet)
    print "Beginning {0} password scan against {1}".format(args.project, args.source)
    scanner.scan()
    print "\n{0} Password scan complete.\nOutput written to {1}".format(args.project, args.outfile)
    sys.exit(0)

if __name__ == '__main__':
    main()
