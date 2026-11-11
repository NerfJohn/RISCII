################################################################################
# dasm: main.py
################################################################################

import sys
from typing import List

from AsmFormatter import NumType, immString, instrString
from ImageParser import RawImage, parseAsImage
from InstrParser import InstrFields, parseAsInstr
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
OPT_WERR = "werr"

################################################################################
# Larger pieces of data for the program.
class Model():
    # Values.
    inFile:  str               # input filepath/name
    outFile: str               # output filepath/name
    image:   RawImage          # input image data
    instrs:  List[InstrFields] # parsed instructions
    immType: NumType           # typing to use for immediates
    useWerr: bool              # treat warnings as errors

    # Funcs.
    def __init__(self):
        self.inFile  = ""
        self.outFile = ""
        self.image   = None
        self.instrs  = []
        self.immType = NumType.HEX16
        self.useWerr = False

################################################################################
# Handle CLI parsing.
def __parseCli(mdl: Model):
    # CLI Options.
    options = [
        (Opt.LONER,  OPT_HELP, "print help menu and exit",  tuple([])),
        (Opt.OPTION, OPT_LOG,  "set log verbosity",         tuple([e.value for e in LogLvl])),
        (Opt.OPTION, OPT_OUT,  "set output file path/name", tuple([])),
        (Opt.OPTION, OPT_TYPE, "set output type of immediates", tuple([e.value for e in NumType])),
        (Opt.LONER,  OPT_WERR, "treat warnings as errors", tuple([]))
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
        elif r.arg == OPT_WERR:
            mdl.useWerr = True

    # Check requirements.
    if len(mdl.inFile) == 0:
        MyLog.log(LogLvl.ERROR, "No input file given")
        sys.exit(EXIT_FAIL)

################################################################################
# Handle parsing in the image.
def __parseImage(mdl: Model):
    # Parse in file.
    isGood, mdl.image = parseAsImage(mdl.inFile)
    if not isGood: return

    # Parse instructions.
    MyLog.log(LogLvl.INFO, "Parsing instructions")
    for i in mdl.image.text: mdl.instrs.append(parseAsInstr(i))

################################################################################
# Handle formatting/output of assembly.
def __outputAssembly(mdl: Model):
    MyLog.log(LogLvl.INFO, "= TEXT =")
    for i in mdl.instrs:
        MyLog.log(LogLvl.INFO, instrString(i, mdl.immType, True))
    MyLog.log(LogLvl.INFO, "= DATA =")
    for d in mdl.image.data: MyLog.log(LogLvl.INFO, immString(d, 16, mdl.immType, True))

################################################################################
# Core execution of the dasm program.
def __main():
    # Init model.
    mdl = Model()

    # Execute program- stop for errors.
    for step in [__parseCli, __parseImage, __outputAssembly]:
        step(mdl)
        if (mdl.useWerr and MyLog.wrnCnt) or MyLog.errCnt: break

    # Report results.
    res = "failure" if (MyLog.errCnt or (MyLog.wrnCnt and mdl.useWerr)) else "success"
    MyLog.log(LogLvl.INFO, f"{res}- {MyLog.wrnCnt} warning(s), {MyLog.errCnt} error(s)")
    sys.exit(EXIT_FAIL if res == "failure" else EXIT_GOOD)

################################################################################
# (start of program).
if __name__ == "__main__":
    __main()
