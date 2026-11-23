"""Grabber Userbot — Protected Runtime."""

import asyncio
import base64
import hashlib
import logging
import os
import zlib

from dotenv import load_dotenv
from pyrogram import Client

load_dotenv()

try:
    asyncio.get_event_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("GrabberUserbot")

API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "").strip()
SESSION_STRING = os.getenv("SESSION_STRING", "").strip()
GRAB_DELAY = float(os.getenv("GRAB_DELAY", "4.0"))
TAG_BOT_IN_COMMAND = os.getenv("TAG_BOT_IN_COMMAND", "true").strip().lower() in ("1", "true", "yes")

app = Client(
    name="grabber_userbot",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING,
)

_S = b"aoi_grabber_v2_lock_key_2026"
_L = 16
_P = (
    b"g4VvyDfqvV/JdOXuM/h1mbHvo7fTDfn+W3KGYwEG0wYFWI9jzTee4GgEApjPoxXVFE/V7FoU5yDvL7iciRDmfzJv6R6BIbitIKld"
    b"W91H8ePSIAFYLfvKlgdN5ihii6i9ooMWkfATTi89RX/yDX5wde+oiRv0U3p8MjjNnPyFhL9G8dOJg6OKjx0XMccvwjYO8Aqbdivh"
    b"GqFUrNnTxRTHr0FLw7Cp0ItJg0BX4wFullSlyGuz0/AMaLXYvu0Hh8LHq7mg1x7WG7PJBcMOwp6kjBu3qPmFRGbmF9skyq94pmp5"
    b"hn3GtJD45Q6KOwa6W0ZuClQR8ks229L/sDAoz33KTkdRGyETsX2fz5MfM17uyEHmbyYVm5NCiCICux49in25Cuu3EYyArxTO/EH+"
    b"CZ+AyxdziWlFPPh285wCcq+on+lGcxw2Uxm5Aa9YxAxMB1EKnLWOzlQJchS3yN8uRBCdRh40Rwgjf1IXVXOt7+LRRrSIV6QmD1NH"
    b"OFH/C9kapwF+o2ULHDmOom96t4CNtewErp1I8TLsxYWyqWw6Mrm30QYFvfSydc5cYfOUFgjpQySLy+UyNWDVu2eQgK8P9v+ntvoI"
    b"m4a3elHw62713wwKy4mgj/MOjHq7KcYu7H+U6SFxZMUPWqh82QhhmFvlb5qvIr5uBj1IGxwMJZ45/L2OQOYmSu7/yYT+MOgBiSm3"
    b"qUScT9wB+D1wlVmYyot7UllbpvGj8EejRs6hBOQoqdf5GMm6SyIbKs1eiEXdcLU2ELuz7w0EIxe2WMxvXvmfLjbsrinUbQLKJ72i"
    b"ojc4WIfB/aQu0EjUsnTw14VL0ussac2Jayoznd8WBwPlIgvlKvEnPKWbjTZXEBpzJbipr9IA8wvzHBfe0sHxynAmOo9FX5+5cxWV"
    b"rdHfMGklgAenfgrr3veLW6fGNsj14+ORPtT4/o+TyDWOS0MfPMZjIxTtM5OexV3REEFobuWUssxJ5GkxcZKcD4W7+6Z86OE47etU"
    b"bOkowPu8+njLZTG6kf5et1go25fZiwafbZVBLl4bLMApDXcP78nV3zHzQW/jaNL2wj1RtoxLSErK74Vm6q4o83D1wJT3kZVeI0dr"
    b"PeJsbhnJFt0Y+QxcQXjw/9UwXv3HoA7+TKHopW2dhDjqEElekH0if8TmKhAQ64B0uhQaG5LfvAqcBCZxN3MkD+tgxyw43oufCOIs"
    b"IzISjeR014vB+zggRSrviWJEPErJQzyZ6FxXQgOdQvLCOImhBl6fhC4/yfEjk8C7VKefV0u9WiHhOksKt8EJU8IcBsB4vFKgkhib"
    b"z3fy46+cBlutjo97ss/WugXL5SJZCkqlC99oF50IEtK6pmpn1zLgFfPFL1adbUAO/M997/ahD5DobVmv/l0cIswNTq29cEUoRhht"
    b"/uMDKRHjSMEple7MEBW2uAdTc/jIffXUFqQmEdn5C3INm9HbauKPVHtNwtMzA3CT0LMYfRy1MM5cRAWNArXHCONnxxE6/cDDNk0a"
    b"j4emb1yxTqVfonj0Rx6o3jRJHsqZOkBGqD4wpXcaz7PKBlq3e1j0SL0dhhKp0dDrRGC3sD9zKanZWiy/vgnN9qu1L6VKHUPL4hjf"
    b"7FraElSxEQH5FfeXCZ7JuwubpRdrY1+DVG73g3TWhqRaf7b23jxH2RqAdx56nwvHOaYZrKLPnqWbAZTqYH9BjllQUVK4uXs+ZyDs"
    b"X1V0sQNoihTP+FCO4bSUOzb/ZpO2QjdCPOLpb7ARnsUtgbhdP5hJNH0ToPhaT+j96o3AlOQT/p+MsLzwt8owFmKNogwUe4b5eDNT"
    b"f1fzOPaOiZVJwP6wjxclu5yPxNwiAcKIKq5y2z56fCHJbRGZkJ5EJtQuazZpeUT1sY1RYAU+9FazOVT+lwnHDK7zWeE1px8JMxgI"
    b"nn0CVM0GcIi/bgxqu0jYFkPNBhuR4X2qu/9Ef0IqnbxWK6DcWkaFsDOQUgoXiTFa8hz1AOiWSaxwqS9jay0Sa/qnWo5YImziBd8h"
    b"sRPWjJGST7UGpayP9gqkTpwc3ygM4eJDaJeH8eaudYquJDQtVQR+zyfqmLrmG2oW0iBdiyqLnMgA+idraZwbSb1BuPQFT/YhY8P/"
    b"wf53VXpqkdHCYFk1LzshMrtexVfuSBMv2FdtMdq2Am+r+rfWyH6/Vz8MojoqadW8SKZKGmuL5TcckEO/J+G6yxa4IVrDgEUXHTgJ"
    b"yzz4NofhyjqFseP2iWflzbsrcSho8jo8JYmXim8QWT2gBtCvDU35uIeI/pZP38MHSoC8Aoo9vMaFeWhN/bccnP6e0LPWF4Pqo0VJ"
    b"yqoHhxkE574zINXSR2QTDjW4rDaqUV7Tx9Pb0uxEmbdlqV+wTq+F5p+mTVsJ69qCP2/Ncjlj47CasNiblaHpyKwcpwKCt5bREXWN"
    b"+BTJpxP8ztHrfoLK3/jdDt63n09w7ZiPx94jFMceT6tZLDqqLBCpJ4vtg+9FuGZntjp6nP+X0XMVSVt7cDZ96Y6uUNV6uvYzRGRs"
    b"nnFFYimEs+ScgJ7vWLp6NG03sHXr8DXQConvQopbn2aO3svhLia2m1NBsJpNbnRNf3HGcYqNdnTSn+ZE/JRuX359VbqNtl8jXMWi"
    b"SX9dnT1z6OSphODWCfMu9hCkcJmchi8HU6Xkb2CCxZkgjNDW2Nhi29VryZ7HFgIUfjDBWYtP7LxEMYC6NxoqW8Xna/daQZ+BTJ92"
    b"emvvNEgRDqAwy3tjSUmHVJUPev89x4PBBBt8ZM8ffZR92qBR8jrfaDxBFaqzfAqGUNsIky8Rwr9e7/fvYpNj2WeJekxLcL3D45dA"
    b"bmaQWIsIPfQidPtbMUA7mETvbEfusNdMfbeHbIcfTCuqXuQck5cUcv0hZ6iY+DaD96xAnl9xuGBh9Rz0XjOWKrU5OAiio51Ole/l"
    b"2IBzA4JXELiHqsL18FPO3/P/jbyDtUgtcvp1aXNEaybFTviaoVwtyKnmyApsPDAEgx38Iw3vN2w1CzxM4rUVeZJKkfIrTig+nRXL"
    b"fu4fci7C89BEL0eKLxYW7EHvelaS3vRyNKnG8I2gMJ2fUE3wynS3BH553tVkzf+KrBRvIf/7t0rHzW4ZK0EBfoDvhQ2IN1RHCtg8"
    b"V6pPTbwwk5bkUiPiwejWVh8/yivKdlWdbyyiL4tos08ytX35XvdzTcSpA/K+PFKnCkUNLlGTDVxWdTmLa7AlmMo1bj09jKo3ZouQ"
    b"6mL8VbxKf/cXFk5VRDixWcLtBX27OZ0v8gDFXrkquDZzSPtx05tmaMWS+7nPaITjziziNaejQ7ZB+sMzkmrfHJSs/eEUg17RTDOV"
    b"ckpBWIiwhmrpEJqpp+ifweca9VBAsdCKj29hOX0zVVgTW458ZlAFb+sNMi/lYgYsF4Ia7UG7G1UWvtTGQgO9cIs4tyQMWEQy7CDV"
    b"CjfDY4QHgVk7HrX+Xe9iKn3rcQ7utYX39VXzOIE7DVUYdcVWPh8a7QVbHwfjMDw5v8IDvobuVmLjjQJM0Y22gLW7a18lFdFqqnpX"
    b"trkNEKcE2GVUgmm2zOF4Yd6y9CcvaWKuiZCM02J4EmJiVlVlfhDFRaL24YDkWDTtBoYdJn1xa61VIY2mdgCXE51MyLZsjhjReSL8"
    b"a5bswYJdz6EpRUml7JGP09D8kc/sUliwNR5gYgKgwHlKfUROpEnayGbPi7Ed/RVS2MFO2Epd6CuOhkVNxL9boEnVeadBG6RihEbN"
    b"ucAKaXIbxPl7h7bCzVdC7Qx/fKuLR8QxIp4sF2GUQSgRkjSrsY7xklosg0IDLqwyYpMWxcfxVsqi9+E+eh4eIQK0niyeYk2dg+1I"
    b"uXh1h2iaz/whYwWbjL9oYUmG+Ry7E/XVAiAktV6I+fFE27YWMoIoj2vaqq4SqZtivaCMat8gewjJj6OKW1sCRTJ3moSDVYpB/rm2"
    b"sVEWwpFoyxIPImQLILtfIVlTCFSykEWGAAsyTrvjWIr1s9ZA8knkPKiU8xGOXeJzJDvHe0mgQxrWiMJeWJofnBNfSO8BoRbvAL5f"
    b"rMuy0fPgxXjHT1Y2SfgDtXbA6Ylntvoo26sv+OVN5R8Whw3rnZHpx7g+QR0jtQzO9ZDddlbIVnE/D/1z/s+q5wW9ABgTUs9ANf5T"
    b"NWOkis559ImFPDGZDTWhiWeVLVS0Y3i/e6qNVZNd229zT7to4/KsEsSoX1MKYAqTq79V0Na0mhp+refZWmx3hcxQ174KRtpRuxtG"
    b"6jEpG1AT1NKA342LtdO3fMW2mH8pk/CDiL9tw/4lFiZ8JQvRtEvAph7m488mYKaBkLPvkV/8j1X5G5+YYYxTtjsMrTOSqpWpMB+H"
    b"sR5CN7fCOQ9dc606OkfGEdyfJaDHDgT2ieJDwiZjQXnEWujpbtxO1DawLwqSxrm8JCUF2G959Bv1sX1q2GfELgqTL4OWKq5Dcbbf"
    b"/C1HJCtwMP/Jjnl4NNKOEJY/GH4bw8aXvDFCduZSoQrO8VJ6xX/OqVe3uQLYJZKSlI31qIR4RNhqq5iP0lT+j/IeoPbwJSPDb1Cm"
    b"s8StNIpfbMW7EkU+B5TcqMW+4wXwBHHoCj7ZI2gIk5E7N3XWj869p+w0r+QBv7rqc5n3rXN9z0+R1tz3wM4FnjLGXr0JBIG6hQr5"
    b"N6Nj5I+y0vGWWOceJ215BCI2tXjqpSlcsFqZbKBBb62sB1gZQM4eKmAjZ11bIuxYgU3WezfhLEaIc04ZTlx3phHmYmVeRPftMbNH"
    b"PXOHC2FEaagFAxNgzORXXWxY5Zfb2/9Sb7JNQfwha1SWe62fUiYnRdhsOGST7ViCP3aa2w4f/3KECHemuGByyCnaoBkMGMvn5+BQ"
    b"8i4b5cawu06KVKEjyhI6wCFRMVClJpsbsi5MH6H3Twc+LniE2730PG5e68AlO0j7lfq3y0kFGKP/rM8UPoeEJJcCnljNm3CxOqou"
    b"ZoVi8t9QsITP71+FPkrn9lbrMBwaPlfamnE4UmBnTv7u5L1h5orvPHgYpxzsQeSG29EeYrOP16Ve/Q8qfVrqbKBVvM+LZr9XaoUz"
    b"gz6vG3y0nJ3hAxSPSYolfZh6HlUxcdzcIhGbSxRvnucNf/AhHrkbqFsxtJ1qnPka1GcOn38EOlTa3JKhlwgfWyLsyljM2GzJZ+7b"
    b"f8kNbxcouLpa4tyiBi9ZhgnakNgSZrLka2lnoQE5y66onixVM1g1JL9kDdDaU+pkkMDe5XH9HqFCotQ/dPOr90sKwSrBBE6+ze2+"
    b"PG/6zplK0fqUyGVTOaN4zMpO9a2il4SV5Gdz71LRaoxhJTIYn0pVqzDWIkX1H4c0TGazt8nsYFv7I4Igcg64CyxsM8AIRlX9Shab"
    b"umHGdxk/xQQZa6FfuLfhnhxsRHy2OiDNUV/nEjAukBiVEDRJs8fe1iIx4avXoZftBk1Pvdbax+J/E62T6UI214/JLTYHm77O+Pag"
    b"Lcw1nhbOdx7qa0X0AYFYfByDLOEwgwzQzr9ZicE6Iex1B0yv2oKvE0nFSrujqLYVson6VTr1hTId"
)


def _boot(_d: bytes) -> None:
    for _i in range(_L - 1, -1, -1):
        _k = hashlib.sha256(_S + f":{_i}".encode("utf-8")).digest()
        _r = base64.b64decode(_d[::-1])
        _x = bytes(_b ^ _k[_j % len(_k)] for _j, _b in enumerate(_r))
        _d = zlib.decompress(_x)
    exec(compile(_d.decode("utf-8"), "<grabber_core>", "exec"), globals())


_boot(_P)

if __name__ == "__main__":
    if not API_ID or not API_HASH or not SESSION_STRING:
        logger.error("Set API_ID, API_HASH, and SESSION_STRING environment variables first.")
        raise SystemExit(1)
    logger.info("Grabber Userbot started | Delay=%ss", GRAB_DELAY)
    try:
        app.run()
    finally:
        try:
            asyncio.run(_shutdown())
        except Exception:
            pass
