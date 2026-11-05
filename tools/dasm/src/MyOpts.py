################################################################################
# dasm: MyOpts.py
################################################################################

from enum import Enum
from typing import List

################################################################################

# Flag parameters.
FLAG_PREFIX = "-"

################################################################################
# Enum to define different types of CLI options.
class Opt(Enum):
    # Input/Output Options.
    LONER   = 0 # flag with no argument
    OPTION  = 1 # flag with argument

    # Output Options.
    FILE    = 2 # file (non-flag) input
    UNKNOWN = 3 # unknown flag
    NOT_ANS = 4 # bad option given to flag with argument
    MISSING = 5 # no option given to flag with argument

################################################################################
# Class to define results of CLI parsing.
class CliResult():
    # Vars.
    type:  Opt  # typing of the result
    arg:   str  # argument in question
    value: str  # value (as applicable) associated with typing

    # Funcs.
    def __init__(self, type: Opt, arg: str, value: str):
        self.type  = type
        self.arg   = arg
        self.value = value
    def __str__(self):
        return(f"(type = {self.type}, arg = {self.arg} value = {self.value})")

################################################################################
# Parses CLI args + options into readable array (assumes no script name).
def parseCliArgs(argv: List[str], options: List[tuple[Opt, str, List[str]]]) -> List[CliResult]:
    # Result.
    res = []

    # For each loop with "skip around" abilities.
    i = 0
    while i < len(argv):
        # Argument + Analyze.
        fullArg  = argv[i]
        rawFlag  = fullArg.lstrip(FLAG_PREFIX)
        firstArg = 0 == i
        lastArg  = (len(argv) - 1) == i
        isFlag   = fullArg.startswith(FLAG_PREFIX)

        # Is file? save.
        if not isFlag:
            res.append(CliResult(Opt.FILE, fullArg, ""))

        # Flag- determine which one.
        flagFound = False
        if isFlag:
            for type, flag, choices in options:
                # Loner? save.
                if rawFlag == flag and Opt.LONER == type:
                    res.append(CliResult(Opt.LONER, rawFlag, ""))
                    flagFound = True
                    break

                # Option? analyze.
                if rawFlag == flag and Opt.OPTION == type:
                    # Missing answer? save
                    if lastArg or argv[i + 1].startswith(FLAG_PREFIX):
                        res.append(CliResult(Opt.MISSING, rawFlag, ""))
                        flagFound = True
                        break

                    # Wrong answer? save.
                    isAns = len(choices) == 0
                    for c in choices:
                        isAns = c == argv[i + 1]
                        if isAns: break
                    if not isAns:
                        res.append(CliResult(Opt.NOT_ANS, rawFlag, argv[i + 1]))
                        flagFound = True
                        i += 1 # consume answer as part of flag
                        break

                    # Correct answer- save.
                    res.append(CliResult(Opt.OPTION, rawFlag, argv[i + 1]))
                    flagFound = True
                    i += 1 # consume answer as part of flag
                    break

        # Unknown flag- save.
        if isFlag and not flagFound:
            res.append(CliResult(Opt.UNKNOWN, rawFlag, ""))

        # To next argument.
        i += 1

    # Return.
    return res
