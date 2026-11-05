################################################################################
# dasm: main.py
################################################################################

import sys

from MyOpts import Opt, CliResult, parseCliArgs

################################################################################

# Exit Parameters.
EXIT_GOOD = 0
EXIT_FAIL = 1

# CLI Parameters.
OPT_HELP = "h"
OPT_LOG  = "ll"
OPT_OUT  = "o"

################################################################################
# Handle CLI parsing.
def __parseCli():
    # CLI Options.
    options = [
        (Opt.LONER,  OPT_HELP, tuple([])),
        (Opt.OPTION, OPT_LOG,  tuple(["quiet", "error", "warning", "info", "debug"])),
        (Opt.OPTION, OPT_OUT,  tuple([]))
    ]

    # Parse CLI.
    results = parseCliArgs(sys.argv[1:], options)

    # Handle results.
    for r in results:
        # Errors.
        if r.type == Opt.UNKNOWN:
            print(f"Unknown flag '{r.arg}'")
            sys.exit(EXIT_FAIL)
        elif r.type == Opt.MISSING:
            print(f"Missing argument for '{r.arg}'")
            sys.exit(EXIT_FAIL)
        elif r.type == Opt.NOT_ANS:
            validAns = []
            for type, flag, vals in options:
                if r.arg == flag: 
                    validAns = vals
                    break
            print(f"Invalid argument '{r.value}'")
            print(f"Arguments = {validAns}")
            sys.exit(EXIT_FAIL)

        # else.
        print(r)

################################################################################
# Core execution of the dasm program.
def __main():
    __parseCli()
    sys.exit(EXIT_GOOD)

################################################################################
# (start of program).
if __name__ == "__main__":
    __main()

"""
options:
    FILE
    LONE_FLAG
    OPT
"""