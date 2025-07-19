import logging
import os
#
###################################################################################################
###################################################################################################
################################################################################################### Module
#
from utils.config    import MUST_LOG_TIME_MS, MUST_LOG_TO_CONSOLE, MUST_LOG_TO_FILE
from utils.config    import MIN_LOGGING_LEVEL_CONSOLE, MIN_LOGGING_LEVEL_FILE, LOG_DIR
from utils.datetimer import now_yyyy_mm__dd_hh_mm_ss, now_local
#
###################################################################################################
###################################################################################################
################################################################################################### Formatter
#
class CustomLogFormatter(logging.Formatter):

    """Formatter that uses the user's timezone-aware time from the datetimer module."""

    EMOJI_MAP = {
        "DEBUG"    : "🪲",
        "INFO"     : "ℹ️",
        "WARNING"  : "⚠️",
        "ERROR"    : "❌",
        "CRITICAL" : "🚨",
    }

    def formatTime(self, record, datefmt=None):

        return (now_yyyy_mm__dd_hh_mm_ss(ms=MUST_LOG_TIME_MS))
    #

    def format(self, record):

        record.asctime   = self.formatTime(record)
        emoji            = self.EMOJI_MAP.get(record.levelname, "")
        record.levelname = f"{record.levelname}{emoji}"
        return (super().format(record))
    #
#
###################################################################################################
###################################################################################################
################################################################################################### Handler
#
class CustomFileHandler(logging.Handler):

    def __init__(self, base_name="qat"):

        super().__init__()
        self.base_name     = base_name
        self._current_date = None
        self._file_handler = None
        self._update_handler()
    #

    def _get_log_path(self, date_str):

        filename = f"QAT_Logs_{date_str}.log"
        return (os.path.join(LOG_DIR, filename))
    #

    def _update_handler(self):

        today = now_local().strftime("%Y_%m_%d")
        
        if (today != self._current_date):

            if (self._file_handler):

                self._file_handler.close()
            #

            self._current_date = today
            log_path           = self._get_log_path(today)
            self._file_handler = logging.FileHandler(log_path, encoding="utf-8")
            self._file_handler.setFormatter(self.formatter)
        #
    #

    def setFormatter(self, fmt:CustomLogFormatter):

        self.formatter = fmt
        self._file_handler.setFormatter(self.formatter)
    #

    def emit(self, record):

        self._update_handler()
        self._file_handler.emit(record)
    #
#
###################################################################################################
###################################################################################################
################################################################################################### Logger
#
def get_logger(name:str="qat_logger",
               min_level_console = MIN_LOGGING_LEVEL_CONSOLE,
               min_level_file    = MIN_LOGGING_LEVEL_FILE,
               console_log:bool  = MUST_LOG_TO_CONSOLE,
               file_log:bool     = MUST_LOG_TO_FILE
    ) -> logging.Logger:

    """
    Return a logger that outputs to console and a regenerates daily log file.
    Regeneration is done at 00:00 based on the user’s configured timezone.
    """

    logger = logging.getLogger(name)

    if logger.hasHandlers():
        
        logger.handlers.clear()
    #
    logger.setLevel(logging.DEBUG)


    if (console_log):

        formatter = CustomLogFormatter("[%(asctime)s] [%(levelname)s] [%(name)s_`%(lineno)s`] [%(message)s]")

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        stream_handler.setLevel(min_level_console)
        logger.addHandler(stream_handler)
    #
    if (file_log):

        formatter = CustomLogFormatter("[%(asctime)s] [%(levelname)s] [%(name)s_`%(lineno)s`)`] [%(message)s]")

        file_handler  = CustomFileHandler(base_name=name)
        file_handler.setFormatter(formatter)
        file_handler.setLevel(min_level_file)
        logger.addHandler(file_handler)
    #

    return (logger)
#
###################################################################################################
###################################################################################################
###################################################################################################
#