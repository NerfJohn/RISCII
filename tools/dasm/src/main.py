################################################################################
# dasm: main.py
################################################################################

import sys

from MyLog  import LogLvl, MyLog
from MyOpts import Opt, parseCliArgs

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
        (Opt.OPTION, OPT_LOG,  tuple([e.value for e in LogLvl])),
        (Opt.OPTION, OPT_OUT,  tuple([]))
    ]

    # Parse CLI.
    results = parseCliArgs(sys.argv[1:], options)

    # Handle results.
    for r in results:
        # Errors.
        if r.type == Opt.UNKNOWN:
            MyLog.log(LogLvl.ERROR, f"Unknown flag '{r.arg}'")
            sys.exit(EXIT_FAIL)
        elif r.type == Opt.MISSING:
            MyLog.log(LogLvl.ERROR, f"Missing argument for '{r.arg}'")
            sys.exit(EXIT_FAIL)
        elif r.type == Opt.NOT_ANS:
            validAns = []
            for type, flag, vals in options:
                if r.arg == flag: 
                    validAns = vals
                    break
            MyLog.log(LogLvl.ERROR, f"Invalid argument '{r.value}'")
            MyLog.log(LogLvl.ERROR, f"Arguments = {validAns}")
            sys.exit(EXIT_FAIL)

        # else.
        if r.arg == OPT_LOG: MyLog.setLvl(LogLvl(r.value))

################################################################################
# Core execution of the dasm program.
def __main():
    __parseCli()
    MyLog.log(LogLvl.QUIET, "can print")
    MyLog.log(LogLvl.ERROR, "can print")
    MyLog.log(LogLvl.WARNING, "can print")
    MyLog.log(LogLvl.INFO, "can print")
    MyLog.log(LogLvl.DEBUG, "can print")
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