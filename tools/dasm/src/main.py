################################################################################
# dasm: main.py
################################################################################

import os
import sys
from typing import List

from AsmFormatter import NumType, immString, instrString
from ImageParser import RawImage, parseAsImage, WORD_SIZE_BITS
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

# File Paramters.
FILE_DELIM = '.'
FILE_OTYPE = '.dasm'
FILE_DIV   = '=' * 80
FILE_LF    = '\n'

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
    if len(mdl.outFile) == 0:
        idx = mdl.inFile.rfind(FILE_DELIM)
        if idx < 0: mdl.outFile = mdl.inFile + FILE_OTYPE
        else:       mdl.outFile = mdl.inFile[:idx] + FILE_OTYPE

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
    # Check output file.
    MyLog.log(LogLvl.INFO, f"Writing '{mdl.outFile}'")
    if os.path.exists(mdl.outFile) is True:
        MyLog.log(LogLvl.WARNING, f"Out file '{mdl.outFile}' already exists")
        if mdl.useWerr: return

    # Begin writing to file.
    MyLog.log(LogLvl.DEBUG, f"Opening '{mdl.outFile}' file")
    with open(mdl.outFile, "w") as f:
        # Header.
        MyLog.log(LogLvl.DEBUG, f"Writing file header")
        hdr = [FILE_DIV, f"dasm: {mdl.inFile} ({mdl.image.origSize} bytes) -> {mdl.outFile}", FILE_DIV]
        for l in hdr: f.write(l + FILE_LF)

        # Text section.
        MyLog.log(LogLvl.DEBUG, f"Writing text section")
        txtHdr = [f"TEXT SECTION ({len(mdl.image.text)} words)", FILE_DIV]
        for l in txtHdr: f.write(l + FILE_LF)
        for i in mdl.instrs:
            f.write(instrString(i, mdl.immType, True) + FILE_LF)

        # Text section.
        MyLog.log(LogLvl.DEBUG, f"Writing data section")
        txtHdr = [FILE_DIV, f"DATA SECTION ({len(mdl.image.data)} words)", FILE_DIV]
        for l in txtHdr: f.write(l + FILE_LF)
        for d in mdl.image.data:
            f.write(immString(d, WORD_SIZE_BITS, mdl.immType, True) + FILE_LF)
        f.write(FILE_DIV + FILE_LF)
    MyLog.log(LogLvl.DEBUG, f"Closed '{mdl.outFile}' file")

    # Delete file on mishaps.
    if (MyLog.errCnt or (MyLog.wrnCnt and mdl.useWerr)) and os.path.exists(mdl.outFile):
        MyLog.log(LogLvl.DEBUG, f"Errors- remove out file '{mdl.outFile}'")
        os.remove(mdl.outFile)

################################################################################
# Core execution of the dasm program.
def __main():
    # Init model.
    mdl = Model()

    # Execute program- stop for errors.
    for step in [__parseCli, __parseImage, __outputAssembly]:
        step(mdl)
        if (MyLog.errCnt or (MyLog.wrnCnt and mdl.useWerr)): break

    # Report results.
    res = "failure" if (MyLog.errCnt or (MyLog.wrnCnt and mdl.useWerr)) else "success"
    MyLog.log(LogLvl.INFO, f"{res}- {MyLog.wrnCnt} warning(s), {MyLog.errCnt} error(s)")
    sys.exit(EXIT_FAIL if res == "failure" else EXIT_GOOD)

################################################################################
# (start of program).
if __name__ == "__main__":
    __main()
