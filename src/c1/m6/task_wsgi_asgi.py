"""
I use gunicorn for WSGI, uvicorn for ASGI.
"""

from typing import Any

import aiohttp
import requests

EXTERNAL_API_URL = "https://api.exchangerate-api.com/v4/latest"


# fmt: off
# более логично динамически получать список доступных валют через API,...
# ...но там ключ нужен, поэтому решил просто хранить доступные валюты в таком виде
AVAILABLE_CURRENCIES = {
    "AED","AFN","ALL","AMD","ANG","AOA","ARS","AUD","AWG","AZN","BAM","BBD","BDT",
    "BGN","BHD","BIF","BMD","BND","BOB","BRL","BSD","BTN","BWP","BYN","BZD","CAD",
    "CDF","CHF","CLP","CNY","COP","CRC","CUP","CVE","CZK","DJF","DOP","DZD","EGP",
    "ERN","ETB","EUR","FJD","FKP","FOK","GBP","GEL","GGP","GHS","GIP","GMD","GNF",
    "GTQ","GYD","HKD","HNL","HTG","HUF","IDR","ILS","IMP","INR","IQD","IRR","ISK",
    "JEP","JMD","JOD","JPY","KES","KGS","KHR","KID","KMF","KRW","KWD","KYD","KZT",
    "LAK","LBP","LKR","LRD","LSL","LYD","MAD","MDL","MGA","MKD","MMK","MNT","MRU",
    "MUR","MVR","MWK","MXN","MYR","MZN","NAD","NGN","NIO","NOK","NPR","NZD","OMR",
    "PAB","PEN","PGK","PHP","PKR","PLN","PYG","QAR","RON","RSD","RUB","RWF","SAR",
    "SBD","SCR","SDG","SEK","SGD","SHP","SLE","SOS","SRD","SSP","STN","SYP","SZL",
    "THB","TJS","TMT","TND","TOP","TRY","TTD","TVD","TWD","TZS","UAH","UGX","USD",
    "UYU","UZS","VES","VND","VUV","WST","XAF","XCD","XDR","XOF","XPF","YER","ZAR",
    "ZMW","ZWL",
}
# fmt: on

# --------------------------------------------------------------------------------------


def backend_sync_app(
    environ: dict["str", Any],
) -> tuple[str, list[tuple[str, str]], list[bytes]]:
    if environ["PATH_INFO"][1:].upper() in AVAILABLE_CURRENCIES:
        response = requests.get(EXTERNAL_API_URL + environ["PATH_INFO"].lower())
        status = f"{response.status_code} {response.reason}"
        response_headers = [
            ("Content-Type", response.headers.get("Content-Type")),
        ]
        data = [response.content]
    else:
        status = "404 Not Found"
        response_headers = [("Content-Type", "text/plain")]
        data = [b"Not Found"]

    return status, response_headers, data


def wsgi_app(environ: dict[str, Any], start_response: callable) -> list[bytes]:
    status, response_headers, data = backend_sync_app(environ)
    start_response(status, response_headers)
    return data


# --------------------------------------------------------------------------------------


async def backend_async_app(
    scope: dict[str, Any],
) -> tuple[int, list[list[bytes]], bytes]:
    if scope["path"][1:].upper() not in AVAILABLE_CURRENCIES:
        status = 404
        headers = [[b"content-type", b"text/plain"]]
        body = b"Not Found"
    else:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                EXTERNAL_API_URL + scope["path"].lower(), timeout=10
            ) as response:
                status = response.status
                headers = [
                    [
                        b"content-type",
                        response.headers.get("Content-Type").encode("utf-8"),
                    ]
                ]
                body = await response.content.read()

    return status, headers, body


async def asgi_app(scope: dict[str, Any], receive: callable, send: callable) -> None:
    if scope["type"] == "http":
        _ = await receive()  # не использую, т.к. код ориентирован на "get" запросы
        status, headers, body = await backend_async_app(scope)
        await send(
            {"type": "http.response.start", "status": status, "headers": headers}
        )
        await send(
            {
                "type": "http.response.body",
                "body": body,
            }
        )
    else:
        return
