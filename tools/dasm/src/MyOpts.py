################################################################################
# dasm: MyOpts.py
################################################################################

from enum import Enum
from typing import List

from MyLog  import LogLvl, MyLog

################################################################################

# Flag parameters.
FLAG_PREFIX = "-"

# Print parameters.
PRINT_MAX = 80 # ideal max characters per line
DESC_MIN  = 20 # min characters per line in descriptions

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
# Summary of CLI options (Option type, flag, description, option choices- empty for any).
CliOptions = List[tuple[Opt, str, str, List[str]]]

################################################################################
# Prints CLI options as a help menu.
def printHelpMenu(desc: str, usage: str, options: CliOptions):
    # Constants.
    INDENT = 2

    # Prep options.
    optionStrings = []
    for type, flag, blurb, choices in options:
        # Format of flag.
        format = (" " * INDENT) + FLAG_PREFIX + flag + " "

        # Format of arg.
        arg = "<arg> " if type == Opt.OPTION else ""

        # Description of flag.
        flagDesc = blurb
        if Opt.OPTION and (len(choices) > 0):
            flagDesc += f" (choices = {choices})"

        # Save.
        optionStrings.append((format, arg, flagDesc))

    # Analyze options.
    maxFormatLen = max([len(f) for f, a, b in optionStrings])
    maxArgLen    = max([len(a) for f, a, b in optionStrings])
    blurbLen     = max(DESC_MIN, PRINT_MAX - maxFormatLen)

    # Print menu (as error for visibility).
    MyLog.log(LogLvl.ERROR, desc)
    MyLog.log(LogLvl.ERROR, f"Usage: {usage}")
    MyLog.log(LogLvl.ERROR, "Options:")
    for format, arg, blurb in optionStrings:
        blurbStrs = [blurb[i:i+blurbLen] for i in range(0, len(blurb), blurbLen)]
        MyLog.log(LogLvl.ERROR, format.ljust(maxFormatLen) + arg.ljust(maxArgLen) + blurbStrs[0])
        for i in range(1, len(blurbStrs)):
            MyLog.log(LogLvl.ERROR, (" " * (maxFormatLen + maxArgLen)) + blurbStrs[i])

################################################################################
# Print error for bad CLI result.
def printResultError(result: CliResult, options: CliOptions):
    # Print per error.
    if result.type == Opt.UNKNOWN:
        MyLog.log(LogLvl.ERROR, f"Unknown flag '{result.arg}'")
    elif result.type == Opt.MISSING:
        MyLog.log(LogLvl.ERROR, f"Missing argument for '{result.arg}'")
    elif result.type == Opt.NOT_ANS:
        validAns = []
        for type, flag, desc, vals in options:
            if result.arg == flag: 
                validAns = vals
                break
        MyLog.log(LogLvl.ERROR, f"Invalid argument '{result.value}'")
        MyLog.log(LogLvl.ERROR, f"Arguments = {validAns}")

################################################################################
# Parses CLI args + options into readable array (assumes no script name).
def parseCliArgs(argv: List[str], options: CliOptions) -> List[CliResult]:
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
            for type, flag, desc, choices in options:
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
