################################################################################
# dasm: MyLog.py
################################################################################

from enum import Enum

################################################################################
# Levels of log data.
class LogLvl(Enum):
    QUIET   = "quiet"
    ERROR   = "error"
    WARNING = "warning"
    INFO    = "info"
    DEBUG   = "debug"

################################################################################
# Static log with verbosity controls.
class MyLog():
    # Static level + counts.
    level:  LogLvl = LogLvl.WARNING
    wrnCnt: int    = 0
    errCnt: int    = 0

    # Static funcs.
    def setLvl(lvl: LogLvl) -> None:
        MyLog.level = lvl
    def log(lvl: LogLvl, msg: str) -> None:
        # Prep ranking.
        rank = 0
        for e in LogLvl: 
            e.rank = rank
            rank += 1

        # Skip if 1) silenced 2) set level too low or 3) 'print silent'
        if (MyLog.level == LogLvl.QUIET): return
        if (MyLog.level.rank < lvl.rank): return
        if (lvl == LogLvl.QUIET):         return

        # Print.
        if   (lvl == LogLvl.ERROR):
            print(f"[ERR] {msg}")
            MyLog.errCnt += 1
        elif (lvl == LogLvl.WARNING):
            print(f"[WRN] {msg}")
            MyLog.wrnCnt += 1
        elif (lvl == LogLvl.INFO):    print(f"[INF] {msg}")
        elif (lvl == LogLvl.DEBUG):   print(f"[DBG] {msg}")
