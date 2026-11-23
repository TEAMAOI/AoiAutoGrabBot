"""Grabber Userbot — Protected Runtime (https://github.com/TEAMAOI/Auto)."""

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
MONGO_URI = os.getenv("MONGO_URI", "").strip()
GRAB_DELAY = float(os.getenv("GRAB_DELAY", "4.0"))
TAG_BOT_IN_COMMAND = os.getenv("TAG_BOT_IN_COMMAND", "true").strip().lower() in ("1", "true", "yes")

app = Client(
    name="grabber_userbot",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING,
)

_S = b"aoi_grabber_v3_mongo_lock_2026"
_L = 16
_P = (
    b"=MTZ5YbOl+sU/6RWazP0b0Ujq9uMRj6mxLQ9B1tK+GeD80G1sGDrryNBiFRRCJ9OArSwd/ICY0p6JWS1i6POj5sdm3SYw4zASf3L"
    b"weNh3x3BsGguz8xyxxAmR7bdYznt9if62VvkbXGH9ClpZFbqo8Z2vGXG3oFt5fTR3fgzIoZ7gO+53omCAncRK+FnF9tDPfGlj+9P"
    b"H1bH8tkr77cOZI3BFIcRFVWCjkiH/oZp48PNJKnm5OM1SEd3adA65GWBSGIkFMfgsMD4Ck6GApGwl/sr1zT1bQhipgXol7IOrA3u"
    b"uxEwM8iFZM5cr+DdZGQbz8pt1mxbBJoipR0VwwOzz/yEgIu1qdX9eesqACq4xhS0kdevLZH/1IOAhEnc50OOulFTPYKpypUgnwp1"
    b"nIA7X29aobKs7s5nmw/keFCtxXfNABAQ1tTgNYhoPxDIEmhhxLMuRHzhvzulWHPv0R3oOSVD3sXfEZziwQm//h3srScCCmNOLR4s"
    b"uSqssDD2oHkftp9s+sVgC/cIhl50hiOMAVBIksZfjmigndVN8irzLh/gvm7+oQ83rJVFbNnb3NIWKvfFPAaVtHE+VJc0K8hYTyZy"
    b"lM7YgHc/Rz9az+TsWIcj06hZbZCX0xWxOJ1A+NDJAqU3JVn5Fqgv/QMvL9bXhheBFumiLT33i/iTRuSzl9IgSuO0zF2k6C8KfVej"
    b"9kOr/FIb6D7amP2J9iaYttWIreevqiFqn98XTmR4T2FNG3kjpVptHdVriVAshdiIF+cq1FQy/tgXZOm1paoBACe0mBmVnIAoivta"
    b"2nHCvPq/z0/LlJpog7Di5mesJTaX+6bTcoh6PH/76j0zVHdRo8Usq08dya2ZmV6YUPRCgzgDjOmg5H6QQ9kwtCWNzCyXN8wzGxxH"
    b"JiLK98UoGL5Iqmi3r9LjSuazrGXkFFozQZkzSBeP9fGNyJQ63tY5g27VB+IF4VhBxCscpVUTOBZdG8d0x//YGyScHCKmjiDlWoUw"
    b"YgGAL/MKBEy3bSERwueq4Jw7IxrDTxcFzO/c4A0OgtPvyrWzXsBT4sSII9EJ9QpYNnvu4LzrfMpYJ/xTqA+o2F+D3TBULYTyyj4w"
    b"fxAtEO3UArTkqIG9/NbR0OST9d1n7jVwpvC2vdycM+nKZavSX+bFcl44p/851pbXrfM4GDuEmCX55Ml8kThAi3WGsF62bxWe7QB6"
    b"ofJOBb/16r78ettoXWVPsMBelTw8YgZ9M0nnI171gOOZmE5Hj5vmT8PplhUdDUJ0GlH4trHEw0MlUbzRsQX/L7Av3FGbWy9KKc3m"
    b"RNOfPS6/fHmCF+yj4uiShLIYiaYlvCF2udHzUfek7komnx18aoMRCIE/MzbU2i0tmMLJsRjsH55HUZ+6N9FQs0HPRi6l5N/9gJvZ"
    b"RaV10k+gNHaU8ys5dYR/5Qm2g+sXOFXa7y9T5/SSrG6ceB9oHjq2dCkuDYOAFtpQ+x5te2ep3jTysSnoTO1FxKNRlJSPBaWDTE9V"
    b"ciBCudG3LuO61qRPVVtCAtZxeoDA14+7amElsNybWqNCuWGefjpvEOvb0nXMtOyNV+C6IDjg3zixekt7Od1ha4IlOwOscUjYEUG5"
    b"I/rEokYfs+ev0OKzcv5CxoZ9ro5yXLeDKkBKb7/5idkvJTH/9ZYNgkaN48KrjN9UBjxlxFDez5S8oXvfpxFvqTdyoONuURn0YnEI"
    b"I9E7zsM3LJgH9Pm/mZvWPvMKYpnKONi1boZwCC1FVvcd0nmD0xsRuHRcjfQOlRriNMk6SQtf5T5Jz8Cg55Dmy2UTCm++wD65e0up"
    b"Kj+QCTE9tyrWRDIebf/6TenN7yrdN7FBMYt+xIdC3tjYmzlT5n1z1VdAXYZcwErFr57Bw+qMJ9InsSpJPDEAe8E9F01DYT7r1mUG"
    b"svXvxPFxe2R859fx99S31Y7UrU2YE9uty1ZNQ+L8XeQ1/3f0MfVXqqJIof6NRQc31np5U77CgMQmtF6KivxC1UeTDmKMM4QF0lky"
    b"0sy0C5cTvnuNc45W6q6u3sruMbANPAaAHFRtRqUqZ0EVTZMTtxjLhVEG+PHPzclCB4ko6VCgHvd6qRruyV5OwZ6jeAuWADGMYSCp"
    b"IviUymBhKdlr9xduhN223BbWcTgkAUU5+Ipbm4CAuwDDdET6cCIolPNwIBOdju+IpQn6bdwMZ0qHFo02QH7QUvDUEEz8Kmcjyc3b"
    b"Hs1GzTIHRDlzkFwJ7TehAkw1TBqOx12KQ/OyUkqfrtnFqNN3HxYDtA1cvQymLL1JK4iH3VFbz+BoDUpJ1ETFlI4nQD8+ej8NPLnT"
    b"7vZZm3eVScHyUn3NmXyATtji1EdQyxBMAOz23be4Q+oHBnuRs+i6PCJCplGwpybJyP+FWpQyOYlIcVniXjdqioShNDifw/cKMf1K"
    b"Hu3W56XVVmJCI7/Z6wmWrHsryZp5dw7z9n7vUw+g+h3SdwidnrTe8y7wKr9VcsDd3GXGkniBRrR7ouMjl5bY3osjM41GbiJLm537"
    b"VQtzw4KPoCv3TyX+V4I17tCCkoQSVfbq53VjhBjGuy7tgYZBptsGlRrrrAaUggdLW/VgLhicQgOYkZOvdx+6O13wNaE8trApXDvK"
    b"bNzaVT0/eZ+A1WuxqCR46E8XgiXSprKACZgrQM5sN74vdF2dQs6hXCXqANHMPui1fw3bLKuiszWafFtWffl+fHREkZ+62uf8XxkU"
    b"BmyNfDy37RZDaDxb80qCJ7eoXl0T+imzh/kD5xFEBMwVbcRxI1goXh8oYOQmzg2SkqEoZWOBF5oQmpk2r0V5OqMpsnI4g0bGLMjc"
    b"XxlltSQRixPImVczk+5GYz6SQsSXj43BVOQSTvyU5I3WRDtKdbh54sRyiJ7TFW7YJLMccAECMWDMOiRmeKtC5UPMCgrwh/5iE7lR"
    b"YiQQhgUlresLYMXggkP9p5igFc+ElQ/bUy2FTZlOYRKjnJVoVna/dYtzSZSoHHgYDgvRCt1mlPJ7VKTD+l13kkxrxfGEt1O2QAQ8"
    b"9LMyGkruSnDrItd2pP8zOg2ACEZObGA+JoeRI7a6fkmtkYf46m64XICBXX3JolHJQh63kC1vW1fSRKI4eqL+KKIZO9NHBcgX2Lz9"
    b"fz4zXghqYsTQzjcZJEGj62K/d6THhr00pBScrJq0nn38cM1khxf79FXcR+uPJPahD/w5Cmmxq/PfNIaeGOsqg/0ostvHSDINc3E7"
    b"lirqz1B/lQ2YVn6y8GtYkXOJOf1p1fgn6JkgVYeFHzytw6I7za7+89EIlvqgktdRl6rKsuNzBKxf5b+htVsYgueulu9ueVUckRs5"
    b"HNVHD1X/+p5A6OfCrJ8SYFGzA/43kliKS8jKmstGR7nN6roxeKpdxbHkiYrYY2h4ocLlM6D2g4Rr6TvPFXHzJKqEeRv95PKiEXl4"
    b"NH6MX4x/+agBcldo6lhMgXaPum6Qxe9oO5MgFeRfYnuT+gu8rGWkoSddj0bQZigqReHyhMgEHn5uX0FRH16slPDpuNuzCAlIcpRl"
    b"qElazhbD4WIW1wgVk315+Io/1y636cbWqUVCv+ulqop3CV+VOyGC5FWU4Wg6TCrCUC5LSPb+4neH1QInB7EKUnezKtYJw9CJrhc7"
    b"7oVFhbS+N3+8ad3ei1BtJQdKPfCnTewj7kr30WUqui2IZGAaQvz/yZiRCdJ8CpiA4hM61IBcL0jej6q9MhzdqNVsa5U00xEqKL/L"
    b"5D4NkrJ/SlJeKZ9Vz2YNjBesikoq4C/ZYPyAJCAEE9v3YAFsPzJ9RWJBOOXtgAvnFDyiUuxm8AnUS/ihiVP74g+SDpno3Qfjj5qv"
    b"QhwwyLa6tp2zCpLCcHT+USwB3y9Ds45mjrXEYDY+2BGzMdGgk2IljCN+GxBUU6iqCLAKhiSehcCt7Q67bbCHFb6CgE8fskl1hVxi"
    b"REBk01ICZhXDo+5KLqGHHbuJzFiG8UKYESKMEzWzf8p4xKc6McVxK57rnsxIHht6Xi80Fy223tXGMPjuHDNjPzZMlle/9ltv9n8p"
    b"nrPKjOlCiWEiCl4JZ5/AEjmDgiRV0wdYqUlNMYWz560CgJSgw0oBddWOKvGaYL2JydH7pVaWVtXANhk7489F5/BTHkSolI1Fa7iY"
    b"bX8Fa1SOmy2xvx52GdkUdW90pt/JWzMsG1mTILJBUV5LktXIiNo63eeI1SmIra/PEESRlyghS1oX45Z+hg0le8ypgp84wkL/V6Ac"
    b"N02mlxnOd5PRNVjmwiUuxWsTEZ4jJoXZhC1n8PGZmBL3lrfi3iiRKaV47ybQXbC9D/Uhm7bZ3r/lRTNsNQjANd0/1GUuiuPBShtj"
    b"blNiOvuL80ZjhaNTHJWx3xAvmeRe8rskPUizymvwYxx7g+MDkIOA8Wcwbe518CiPG/SS1rEreXfQz1D0FIY0g57nC1ET/vA15jvZ"
    b"h6TQMZ1NP7LP/8GeyBhLm+ihQaqsJmnhCnr4RFVPsx7vaAT1oGlnPRgHcEoHmnMbrLODjgfbXkqDznPmJvW8Z+RkM5X2YphqSy/S"
    b"jQQgsCYa7M0SCKzypthrktX6XMHunwKGNj2drALdxDB1fSiNCqX7Fp/7S3GS5e0px8W8w0fqMUmfnK8gWOI2Jl3FK58B3VFNUc9P"
    b"sNMtbh/Vu+skyBnaUocFXqYFWNBNoJHLMlctJzhCJI/71fths2Uni1Ol3/75UEqnr2EHUGW4CLZoDXQTQxBkIfWZ2m2YBUCBJlhh"
    b"xYJ6OTdcyNwVM/T8R9HhzfIwUElwjge17l6Cmfz1Sn9T/do9eIjtcTWF10C/DkiHytBS7TTTEChtLd657Zc3gPQKUSxiNYXW3Y7H"
    b"5uhkLQ4B3j+b2On6lZccZGS041iGZdqrY2LTwqmndbf7U/uRuR1kl1IPoKMM1V/gX64/MAO3p46qiWCBVwU9A1HEkkXPNwjY8Q/S"
    b"rCSeM3f/0P96fOz6poxkLq9DJ6QZgLBEWyzLb/xgAX98fgZ2jsaE5dajN1BJ0Y/3w5aehgVWIitwsFofyMRSpar8TnkPHc/w5A7w"
    b"oEoFXtH+b0+tdzFsC9uCYqvUI/pAGUbwreo5myVoouZLD13CLePsFGJTRPNNjQhcivLBVI/N4tk8fjQQA6PH1gomLr74p41rJ898"
    b"OUAdfUw8I6A877RKLc/Gr5pNub6WzaRciYrAVTP9/3yL7GUjjmKVwPEQdRZJR+rZWrW2u23UAoaX2gEe9bi5V8xS2bmU3xZiJFiF"
    b"p2QKm49mHeqSjyXgJGdgdLJNJsUA00i55dwvz8OUoKI3iTLU6P1dNlJD7xtQOc8o7lIfbcrUIQ0iUD4wyx4OxLBCDrAtAytIdoaH"
    b"sqmNyPWk47BNmgbVwLVTcbZ+LXLlSDoYJlbezUMjy+eIITwQaAkhzQPCDKcVtAKevu3Myt11+DLJGNJLDFbgTCTp8hm4UsDUtz6W"
    b"lepRLSDBP/coxenh5vHw7Lju0+F1uFUogHcqC3w4Rt64kqwA1oSpNjsU02bIxqqjw+YkvvrubmKPokiihT2nExnkvFA6Vdx5UiDK"
    b"JR55iaKp3vsVDqHBFSfSbW+0gG8sBAOj9tAQJMnOpa0F5E1vEQ2etG1NOPdgrBrROFdVG0MNIKXY/OUWM2pttAFzpg4PnGCa6vA7"
    b"RfCZMhQgZXjogj98edcm12Pm/Qiy6WXlTpORM6NGLLnw2Nu81JootLM9fN3shQnl6ebNI1q0tTDipVNaMkiW9DLDegJ+kHKLVN3w"
    b"vGfWdndwPGFnDRk+/O8VPhj35WW4PFDFk2IjwRH6gRJPwGRVK1IlNcpYBzn4i+SIVuqCnJ1VQik61hJJLOIZKufc2Y1u83y9xGW+"
    b"Trcd7EkiwCC2BmBPJceUgpTKYxgMF9dNLpKslEjmCgXifFCNRJYYl++Z4IB8nSvHqzv2WyucN3jHah9hojDA669ldps5fIbpeSxE"
    b"TLlzJOPSbiAcEnn+sL8oKHO2fSACpOxeb3VkhlnvymgCrb4DjFY8O5Fq/klTFY4AvoIIwEXpPzWysjPRBdMclzRsBvrJBXHupjaa"
    b"oqtFQB75WQKlTz6gtuF48xvdd7SQHsmfUec0MvtbrlMG8umvEysN6iCyz3Ss+wYO9L4sCg8WRcLYGzA8MoBhPKUz53H7wZ9f1u1n"
    b"KlD0kbVVIaaieXWhYkk/fQ0BAnZan5Sm/hTX5gUmFus9p1seyaMw8rRhdsVnN98LowKTBHd5A5oOKml8q8uP4jsFy37ZwPIrUQkB"
    b"XQXuKTyjh+bph8jFp0A4AgsXuv30/UTZvtYo6aZbK02PIulaOb0V1ShQRJ/ozubc2OPW3ldG0ZGBUQjTitsIEC64VMC61MNSBrpR"
    b"sDEzRKOWct2hIAbx9ENdeAFCuLPsHKcCk6hQT3jYwGRw00NsBTQy4Nc/wJh0m45gQgyoZNAjCp/LLUy0lhpH7COSKHQGxQ1VAb/i"
    b"t/JKYpRnDRVkmBPYxAPh/gjUMo4qdoKL+kNn+SjO4ByRFMegqhEORwWCAKvDtXo8MOxN6fmDhCscEdMtGyipOREuQaIruT4wyiMi"
    b"yr81c9Nos8PqQSqK+JbIZ0taTEtgBspCuiV0VYSuazUSzK+/JmzgMCJdV1d1bT2dkHKMNAzHOr25P9T5dqO8Ua4e4ko0OWeF79nY"
    b"FrlcyTtvfiMDOCszrblyNwxa9d4yBf3j6NswoszuQqx/8+EB+elCrbmlBS+q7mtuqWBVjaEOTAK/rSBfWt3d4oiIxCwHO+piYIJ1"
    b"qOps2Z2n5yeSH6NBVNk+r/DHWa9ee5CYeZcRAexUwfmZKDlTypL4FiSfoBkrrWAzk0WCmBHI2zm7aAJnNeu5hXDz4Wgy3VGRrkKY"
    b"nzdZH0JzDBcF/+gMbJXeN8nkKsxlPyG/yKHj/LUvlGphWelBO7kzjItU6yvbpTbv7iLC/pymj3iQINsw4Kyf5n112KjLG/wZ4eR2"
    b"kYhSaHq7kYf+Mv1TVVnTioq4G5UCb7zSD1I5+Q+An71NdTJCnyngatrLtW2izc8yqP3/RzofdVNJrd4mFPoKCptC5udE5PoPlqZ3"
    b"Ac4LC2mNPk7qIMbGcQq4Kn339vJ7pWUa5GgVUySq+t8l7qJkCm+8b6HGR9QKRcdPutNqVTGqZm6JghPjRsUtrMcU6Mp+hsvGponn"
    b"/3uQpID+0bkgKxr07KNWupcj1O50riDap4Tetf54aLrIWaWdxIIqxZC4y+hD4YFAAVCmKrymH1nsSeNexMyFZ04sF+fhK8tTIBoB"
    b"Pdu3xEBb06vZP0sEYDiPjmsyQvotWYhB82vNxZFBAqjdoXwguJZTLZ0xW2BPTi646Hst8jauznILEkAga9tJK6dsGQ+KPOE7HFZo"
    b"jxVnitSPjLw7mPHCDQmK1EGCTtT31yG8DlxbqmYovl7Z9NYMoaMSepekfRzE9PJLPST72b+W5tQrr2yVoYceTyPaygOPiKSRVv9Q"
    b"4L9d01yBUCGqbuo9Ql/q+H7ycjuzPCtEsqb7udO4S2fF+dVqzq2pklRRMFLu2JnfLDOqYgSVQpXknOkvEGWn7/JzwqnHGcmT7rRl"
    b"nwanlNBxVipBapoO5Q00fMHx2SO3nmK0Nc166aw+ydlLzuXzic6HtosGz7UX0SINnSqUI+Sp1VAQ4Qk0fiUrlRmsKuPLtJmdqOts"
    b"OnzkRl7lqSJUDWtqxj1t9a/0iR4m3J0Xb940sQ2sUx1HrU0z1KzTZXzyJOIuOp4u5dxmiTUq8HdEE67j+cgwNKcLoTDHxxTY66S7"
    b"FzAMAp35VrH/oWboT7F8qTTctHHzJwXoDLq4NwLcXn1wkKj3Hcxsv+lGCcX5ZWQA/EqQ2SnGsewuV/CbI638xIHmQSKxFO9v3OeM"
    b"v3N4N+eWtCMHAoD2ZkDYgMP0TqY7U78KbzIQWyPMVsBItbrLhB0c7lXmcw3CqHrM330qSds+y0qTnXlp5s2xov6PEZ5xxJHItmzs"
    b"syeeRPjdwLyHN/MFA0uOhzGvuXYgLLA31Y+LgMIw+3lpSJYjFNV3yhMf8ymegpQp2AbfhNLcwuQ2x9kqnUESWBAdtPmtC5AVxofi"
    b"h4iDv/9EgYKpgV0B3nGQb7LuLgA9Nba68PNtb4+J7FCwj8j+e7f7F/lvLkaBTm3mXhwt31VdH5F74zoss3HKtpQXH4utnmUGHWn0"
    b"Mx+H5iwpm3YjNFZ4MXVMBIy2tsYr51LYQJpQGaVQXvaoZ0lZ/W8INMhnDjRj3kWVxbF8KGdAEyZh11i/RWfsPe3Nqgq4VlPOK88d"
    b"ZBKHAv5EVQBzywH0C9HrTQtIfIh5Nc6X7iO7MQlFGPNqprt7VGmAOPmd79HRmfYwVFty6Qzz7RwIXgD94gHlJiWmzwNbBnWMa1Jc"
    b"iNFTi2Jf0a1Q3hRbF27ZD2bmG+ZagWv4fkxzIA2cx1IglCM5VsDTxT1fw8W/y0EG92J63Q536jEk7zHjG92FpXjl0XmlZ+C59aoz"
    b"9fRl+ZuslWyM9FVYBJxjCZXFnbdnO/19lS+jjz6lWvSE4pjWRkfbE0bUGA3lrYGJYn8fag9UHv7GscG9scSY5aOS+0DM+FwDl/4S"
    b"BXvN1/Wqi+od066DdGupsUxP+zHzHDkE8T7ICLKJR/gfRRjqH/YsrnK17VnnpfHO7Ac2gw6H4p6zSNGQQ2CGco2XofKro9dXDMQg"
    b"Nkv4ESYSdxbvMdIozWLX7mnBIPdxPO8aUUg6WC8Y99qkNaOJjOqtVL4JpKQIXGSvFqflbRa2fFYvD7Dis+tN4m//ObVNlM05AMyY"
    b"fWosMw6YeKTOHcvz51ZTcYNFKSA1GvRofbU3CqLwUCZ4cabvkD4Y1hr/HHJLrNhT+/FhDbKHvbVjDx3Lo2+QJc3keBrvwVMN3XLQ"
    b"HoL41Xg8GYa8zOzx4Gv0YB2b6jnhoZp4b/eqYrOd0oMLBQaw1usB9tqLgDNbI6/3knqtro53lO16UY2TXlYOgIJzwIvZaJFnhiox"
    b"hX820pPRVErWAmyB0I3OZFVQrAIq"
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
    if not API_ID or not API_HASH or not SESSION_STRING or not MONGO_URI:
        logger.error("Set API_ID, API_HASH, SESSION_STRING, and MONGO_URI environment variables first.")
        raise SystemExit(1)
    logger.info("Grabber Userbot started | Delay=%ss", GRAB_DELAY)
    try:
        app.run()
    finally:
        try:
            asyncio.run(_shutdown())
        except Exception:
            pass
