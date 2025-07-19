import os
import asyncio

import json

from curl_cffi import AsyncSession
import re
#
###################################################################################################
###################################################################################################
###################################################################################################
#
from utils.datetimer   import timestamp, now_yyyy_mm_dd, monotonic
from utils.logger      import get_logger
from utils.http_client import get_async_client_ds_screener_infoer

SCREENER_DIR  = os.path.join(os.path.dirname(__file__), '..', 'files', 'screener')
os.makedirs(SCREENER_DIR , exist_ok=True)

SCREENER_REFRESH_RATE_SEC = 60
DS_TOKEN_INFO_ENDPOINT    = "https://api.dexscreener.com/tokens/v1/solana/"
logger = get_logger(name="Screener")
#
###################################################################################################
###################################################################################################
################################################################################################### Screener
#
class Screener:

    DS_RATE_LIMIT_PER_SECOND = 4
    DS_TOKEN_INTERVAL        = 1.0 / DS_RATE_LIMIT_PER_SECOND
    ds_last_call_time        = 0.0
    ds_rate_limit_lock       = asyncio.Lock()
    async def ds_rate_limiter() -> None:

        async with Screener.ds_rate_limit_lock:

            now = monotonic()

            wait_time = max(0, Screener.ds_last_call_time + Screener.DS_TOKEN_INTERVAL - now)

            if (wait_time > 0):

                logger.debug(f"DExScreener rate limiter sleeping for {wait_time:.3f}s")
                await asyncio.sleep(wait_time)
            #

            Screener.ds_last_call_time = monotonic()
        #
    #

    def __init__(self, websocket_url) -> None:

        logger.info(f"Initializing screener")

        try:

            self.websocket_url   = websocket_url
            self.infoer_client   = get_async_client_ds_screener_infoer()

            self.screener_mints  = []
            self.processed_mints = []

            self.final_mints     = self.load_final_mints()
            
            self.latest_refresh  = 0

            logger.info(f"Screener handler initialized")
        #
        except Exception as e:

            logger.error(f"Failed initiating screener handler • {e}")
        #
    #

    def load_final_mints(self) -> dict:

        logger.debug(f"Loading the screener tokens")

        try:

            filename = f"introduced_tokens_{now_yyyy_mm_dd()}.json"
            path     = os.path.join(SCREENER_DIR, filename)

            if (not os.path.exists(path)):

                return {}
            #

            with open(path, "r", encoding="utf-8") as f:

                result = json.load(f)

                logger.info(f"Loaded {len(result)} tokens")
                return {}
                return result
            #
        #
        except Exception as e:

            logger.error(f"Failed loading screener tokens • {e}")
            return {}
        #
    #

    def save_final_mints(self) -> bool:
            
        logger.debug(f"Saving the screener tokens")


        try:

            filename = f"introduced_tokens_{now_yyyy_mm_dd()}.json"
            path     = os.path.join(SCREENER_DIR, filename)

            os.makedirs(os.path.dirname(path), exist_ok=True)

            with open(path, "w", encoding="utf-8") as f:

                json.dump(self.final_mints, f, indent=2, ensure_ascii=False)
            #


            logger.info(f"Saved {len(self.final_mints)} tokens")
            return True
        #
        except Exception as e:

            logger.error(f"Failed saving screener tokens • {e}")
            return False
        #
    #
    ##############################################################
    #
    def decode(self, message)                -> list:

        decoded_text   = ''.join(chr(b) if 32 <= b <= 126 else ' ' for b in message)
        words          = [word for word in decoded_text.split() if len(word) >= 55]
        filtered_words = [re.sub(r'["*<$@(),.].*', '', word) for word in words]
        extracted_data = []
        for token in filtered_words:

            # Check if token contains an ETH address
            if ("0x" in token):

                token = re.findall(r'(0x[0-9a-fA-F]+)', token)[-1]
                # print("ETH: ",token)
            #
            elif ("pump" in token): # Check if token contains 'pump' keyword

                token = re.findall(r".{0,40}pump", token)[0]
                # print("pump: ",token)

                if (token.startswith("V")):

                    token = token[1:]
                #
            #
            else: # Otherwise extract the last 44 characters

                token = token[-44:]
                if (token.startswith("V")):

                    token = token[1:]
                #
            #

            extracted_data.append(token)
        #

        return (extracted_data)
    #

    async def connect_ds(self)               -> list:

        logger.debug(f"Connecting websocket")

        url     = self.websocket_url
        headers = {
            'User-Agent'               : 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0',
            'Accept'                   : '*/*',
            'Accept-Language'          : 'en-US,en;q=0.5',
            'Accept-Encoding'          : 'gzip, deflate, br, zstd',
            'Sec-WebSocket-Version'    : '13',
            'Origin'                   : 'https://dexscreener.com',
            'Connection'               : 'keep-alive, Upgrade',
            'Pragma'                   : 'no-cache',
            'Cache-Control'            : 'no-cache',
            'Upgrade'                  : 'websocket',
        }

        websocket = await AsyncSession().ws_connect(url=url, headers=headers, timeout=10)

        for attempt in range(1, 3+1):

            res         = await websocket.recv()
            message     = res[0]
            pairs_start = message.find(b'pairs')
            

            if (not message.startswith(b'\x00\n1.3.0\n')):

                continue
            #
            elif (pairs_start == -1):

                continue
            #
            else:

                logger.debug(f"Websocket Complete")
                return (self.decode(message))
            #
        #
    #

    async def complete_mint_info(self, mint) -> dict:

        logger.debug(f"Completing info for mint {mint}")

        if (mint in self.processed_mints):

            logger.debug(f"Mint already infoed")
            return (True)
        #


        for attemp in range(1, 4):

            try:

                await Screener.ds_rate_limiter()

                url        = DS_TOKEN_INFO_ENDPOINT + mint
                response   = await self.infoer_client.get(url)
                code       = response.status_code
                json_data  = response.json()[0]

                if (code==200):

                    symbol = json_data.get("baseToken", {}).get("symbol", "BAD_SYMBOL")
                    symbol = re.sub(r'[<>:"/\\|?*]', '_', symbol)
                    self.processed_mints.append(mint)
                    self.final_mints[mint] = symbol

                    logger.debug(f"Mint info data fetched completely")
                    return (True)
                #
                else:

                    self.processed_mints.append(mint)

                    logger.debug(f"[{attemp}] complete_mint_info() Unexpected response • code {code} | {response.text[:120]}")
                    return (False)
                #
            #
            except Exception as e:

                logger.debug(f"[{attemp}] complete_mint_info() Exception during • {e} | {type(e).__name__} | {repr(e)}")
            #

            await asyncio.sleep(1)
        #
        else:

            logger.error(f"Failed to fetch mint info data after all attempts")
            
            self.processed_mints.append(mint)
            return (False)
        #
    #
    ##############################################################
    #
    async def refresh_screener(self)      -> bool:

        logger.debug(f"Refreshing screener")

        for attempt in range(1, 3+1):

            try:

                self.screener_mints = await self.connect_ds()
                logger.debug(f"[{attempt}] Screener websocket data fetched")

                return (True)
            #
            except Exception as e:

                logger.debug(f"[{attempt}] Failed refreshing new pairs • {e}")
            #

            await asyncio.sleep(0.5)
        #
        else:

            logger.error(f"Failed connecting to websocket after all attempts")
            return (False)
        #
    #

    async def refresh_final_results(self) -> bool:

        logger.debug(f"Refreshing final results")

        try:

            await asyncio.gather(*[self.complete_mint_info(mint) for mint in self.screener_mints])

            self.save_final_mints()

            logger.debug(f"Final results refreshed")
        #
        except Exception as e:

            logger.error(f"Failed refreshing final results • {e}")
        #
    #
    ##############################################################
    #
    async def refresh(self) -> bool:

        if (timestamp()-self.latest_refresh < SCREENER_REFRESH_RATE_SEC):

            logger.debug(f"Too early refresh. skipping")
            return (True)
        #

        logger.info("── Screener.refresh() ──────────────────────────────────────────────────────")

        try:

            count = len(self.final_mints)
            await self.refresh_screener()
            await self.refresh_final_results()
            self.latest_refresh = timestamp()

            logger.info(f"Screener refreshed. {len(self.final_mints)-count} new tokens arrived")
            logger.info("── Screener.refresh() complete ─────────────────────────────────────────────")
            return (True)
        #
        except Exception as e:

            logger.error(f"Failed refreshing screener • {e}")
            return (False)
        #
    #
#
###################################################################################################
###################################################################################################
###################################################################################################
#
