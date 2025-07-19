import httpx
from curl_cffi import AsyncSession
#
###################################################################################################
###################################################################################################
################################################################################################### WatchList
#
_client_ds_screener        = None
_client_ds_screener_infoer = None
_client_ds_asset_infoer    = None

def get_async_client_ds_screener()        -> AsyncSession:

    global _client_ds_screener

    if (_client_ds_screener is None):

        _client_ds_screener = AsyncSession()
    #

    return (_client_ds_screener)
#

def get_async_client_ds_screener_infoer() -> httpx.AsyncClient:

    global _client_ds_screener_infoer

    if (_client_ds_screener_infoer is None):

        _client_ds_screener_infoer = httpx.AsyncClient()
    #

    return (_client_ds_screener_infoer)
#

def get_async_client_ds_asset_infoer()    -> httpx.AsyncClient:

    global _client_ds_asset_infoer

    if (_client_ds_asset_infoer is None):

        _client_ds_asset_infoer = httpx.AsyncClient()
    #

    return (_client_ds_asset_infoer)
#

async def close_watchlist_async_clients():

    global         _client_ds_screener, _client_ds_screener_infoer, _client_ds_asset_infoer

    for client in [_client_ds_screener, _client_ds_screener_infoer, _client_ds_asset_infoer]:

        if client:

            await client.aclose()
        #
    #

    _client_ds_screener        = None
    _client_ds_screener_infoer = None
    _client_ds_asset_infoer    = None
#
###################################################################################################
###################################################################################################
###################################################################################################
#
