################################################################################
# dasm: main.py
################################################################################

import sys

from AsmFormatter import NumType, immString, instrString
from ImageParser import RawImage, parseAsImage
from InstrParser import parseAsInstr
from MyLog  import LogLvl, MyLog
from MyOpts import Opt, printHelpMenu, printResultError, parseCliArgs

################################################################################

# Exit Parameters.
EXIT_GOOD = 0
EXIT_FAIL = 1

# CLI Parameters.
OPT_HELP = "h"
OPT_LOG  = "ll"
OPT_OUT  = "o"
OPT_TYPE = "t"

################################################################################
# Larger pieces of data for the program.
class Model():
    # Values.
    inFile:  str      # input filepath/name
    outFile: str      # output filepath/name
    image:   RawImage # input image data
    immType: NumType  # typing to use for immediates

    # Funcs.
    def __init__(self):
        self.inFile  = ""
        self.outFile = ""
        self.image   = None
        self.immType = NumType.HEX16

################################################################################
# Handle CLI parsing.
def __parseCli(mdl: Model):
    # CLI Options.
    options = [
        (Opt.LONER,  OPT_HELP, "print help menu and exit",  tuple([])),
        (Opt.OPTION, OPT_LOG,  "set log verbosity",         tuple([e.value for e in LogLvl])),
        (Opt.OPTION, OPT_OUT,  "set output file path/name", tuple([])),
        (Opt.OPTION, OPT_TYPE, "set output type of immediates", tuple([e.value for e in NumType]))
    ]

    # Parse CLI.
    results = parseCliArgs(sys.argv[1:], options)

    # Handle results.
    for r in results:
        if r.type in [Opt.MISSING, Opt.UNKNOWN, Opt.NOT_ANS]: 
            printResultError(r, options)
            sys.exit(EXIT_FAIL)
        elif r.type == Opt.FILE:
            mdl.inFile = r.arg
        elif r.arg == OPT_HELP:
            printHelpMenu("Disassembles RISCII image into assembly", "(dasm) [options] <input image>", options)
            sys.exit(EXIT_GOOD)
        elif r.arg == OPT_LOG:
            MyLog.setLvl(LogLvl(r.value))
        elif r.arg == OPT_OUT:
            mdl.outFile = r.value
        elif r.arg == OPT_TYPE:
            mdl.immType = NumType(r.value)

    # Check requirements.
    if len(mdl.inFile) == 0:
        MyLog.log(LogLvl.ERROR, "No input file given")
        sys.exit(EXIT_FAIL)

################################################################################
# Core execution of the dasm program.
def __main():
    mdl = Model()
    __parseCli(mdl)
    isGood, mdl.image = parseAsImage(mdl.inFile)
    if not isGood:
        sys.exit(EXIT_FAIL)
    MyLog.log(LogLvl.INFO, "= TEXT =")
    for i in mdl.image.text:
        instr =  parseAsInstr(i)
        MyLog.log(LogLvl.INFO, instrString(instr, mdl.immType, True))
    MyLog.log(LogLvl.INFO, "= DATA =")
    for d in mdl.image.data: MyLog.log(LogLvl.INFO, immString(d, 16, mdl.immType, True))
    sys.exit(EXIT_GOOD)

################################################################################
# (start of program).
if __name__ == "__main__":
    __main()
