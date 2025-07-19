# WARNING: This module is internal. Better not to import or use directly.

from datetime import datetime, timedelta
import time
import pytz
import warnings
#
###################################################################################################
###################################################################################################
################################################################################################### Modules
#
from utils.config import WORKING_TIMEZONE
#
###################################################################################################
###################################################################################################
################################################################################################### Functions
#
def monotonic() -> float:
    
    return time.monotonic()
#

def timestamp(ms:bool=False) -> float:

    """Return current UTC time since epoch."""

    if (ms):

        return (time.time() * 1000)
    #
    else:

        return (time.time())
    #
#

def set_timezone(timezone:str=None) -> None:

    """set timezone string to config."""

    try:

        if (timezone is None):

            WORKING_TIMEZONE = 'Asia/Tehran'
        #
        else:

            pytz.timezone(timezone)
            WORKING_TIMEZONE = timezone
        #
    #
    except Exception as e:

        warnings.warn(f"[datetimer] Invalid timezone '{timezone}'. Falling back to Asia/Tehran.")
        WORKING_TIMEZONE = 'Asia/Tehran'
    #
#

def get_timezone() -> str:

    """Get timezone string from config or default to Asia/Tehran."""

    return (str(WORKING_TIMEZONE))
#

def now_local() -> datetime:

    """Return current local datetime object based on timezone config."""

    tz = pytz.timezone(get_timezone())
    return (datetime.now(tz))
#

def now_iso() -> str:

    """Return local time in ISO format."""

    return (now_local().isoformat())
#

def now_yyyy_mm__dd_hh_mm_ss(ms:bool=False) -> str:

    """Return local time as a human-readable string: YYYY_MM_DD_HH_MM_SS"""

    dt = now_local()


    if (ms):

        return dt.strftime('%Y_%m_%d__%H_%M_%S') + f"__{dt.microsecond // 1000:03d}"
    #
    else:

        return dt.strftime('%Y_%m_%d__%H_%M_%S')
    #
#

def now_yyyy_mm_dd() -> str:

    """Return local time as a human-readable string: YYYY_MM_DD"""

    dt = now_local()

    return dt.strftime('%Y_%m_%d')
#
###################################################################################################
###################################################################################################
###################################################################################################
#