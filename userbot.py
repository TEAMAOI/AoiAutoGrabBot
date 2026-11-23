"""Grabber Userbot — Protected Runtime (https://github.com/TEAMAOI/AoiAutoGrabBot)."""

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
MONGO_URI = (os.getenv("MONGO_URI") or os.getenv("MONGO_URL") or "").strip()
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
    b"=MgGViQGN6bi2LY2LafqRhlQ2Zpmv3YyMPxNJ4+CZcUkiyi5j/HG7VUnNrmbzAB0WJ/PybU+hAE9BLC4c+qNGxGoieejmOFvjzGq"
    b"MDN4otN42i2IMkZSy8W7OKI29hvwW40wz9TIvV5gZEbcnVltuDd18b/sT/4OxX8kOLbRAB6gFhd2crsDJhZiuXiJT5qrAFEynK6v"
    b"+XQoVCvgnw2X2j3Q6oHCvIHavCgHcCoey1J9SZaM8nQdNBJqeIC4uweBMQowkS71WK4MEVc7gxhewzs6uPlgisZsDeoVqjrXFELN"
    b"U4cK22VA5G+0hR5EIkDfLvu7KVR5Tb2OaA0sIm6epSfecwPvyeETa9+pT9xcJVG2Ibo2iGO/bdCjeN2XCi4WIMkb0ftfw5n2QcZY"
    b"jrzp6Df8QIcIjeGPQQ0digJDHwQyY0jI3UdxVph+A6IPYLSB1FP5uWjO79ux87CSvpW9efWufjzEglWtEWDwUngnJpfvZmFrjSq3"
    b"rQwbOi1flhdASscg8Zsm6y9coxgRhtuGCL/odreOSjuakeyVDarDv/9UnS3DBmPvI7RdshhCogNXJ6U6IBat6qYy+EVGmpolgdrr"
    b"DPFtUBPVjLjvWrV8HE5aWFlZs7/KbwIWM2aXJB0rGFksvZflrXOqoynlLkl1rMf7BBOur5ReV09FacB7srqHafzv0bMFfP0579Hk"
    b"0oVp4uPLtApXTFtDNJwHx95KU/WSUJLO0wixDHAo92uz1nSEFuuvtKjGc/ge/aaEtCmIZ3OzX5dJLudWvg7fv7qUjipuUzBXTT0n"
    b"xIfXbthjsIKnj6SBN/Rxg43mnAPknMc+KyZcJce0g5TKV+TJ3LcJU4cD83LAz5YbV9HYUtbknb259l1Q7rvRtvij+R6uxT0HiM8d"
    b"kgReISFjwc4jZ7WNaJerEM38ABkjlIEZqhQ6GIS0m+b5/R7CRrCKDLbM5aCwFaRl5EaGVo+eL3/ej5p1R1oQ3GjM0aB0eqq6tyQ7"
    b"0qQsSvegLl2+dCVytkzJWy00aqfqhBovvxDOkRCHCk+hP/xjJCqAa+hDKgyt9BNxgQgKRFmF4UwuIpYt+9dT9W2mU+UorX8AdhWj"
    b"tM8NAzIOxzvRvqDzm3hIvAdxTwFTvelUwvB46J849hNN6s8mqDNtmcRWTgmjZLg6X3gO7SUCEDfIWYkNPeKGvIy+L0ztvDBrtI80"
    b"MRssPZTJgbeq4tYwm5qwPaSvdB4Po8vol/0CYQQXdsax8058h+hwoaev5EiVnpa2U50itKzmc5AjwcfHt/PHmznMgzpikyeeV1WR"
    b"1YwqtCtCXd+Ybn+YUwm72YbSIYPqBLBlXYPPoNlpoENLMNEaBmZevnADyf9t0RsqZRaiF1cVfsbGc5Ec8KjemiplcdpxiSJZiPJ7"
    b"hT+JNswCW095+lLW/xck7lNrV0vOn93YC7pSf9cMg9pfOUGNH1LEDAqqrN5nElSQeFXf1zp98+4CRlWy26dVBvhjkUENkQzvgdiJ"
    b"rWSojsw8VARQtbpfTQaB7ACPAxG8GyHmDnyfMhsM1aP7Lm2YRjpBBLSjfHmmDx1+eYlw9/HhEERauaQfVTsn5rG8EvCy8/H8RQvM"
    b"KTZKFpwBBY7mvXVRf1gCxBw8ac/A+qnibypTONVQr0BGzEhluhhTtOnxtpWxNqLo0ejG24vH6BaSTwzToyXPhVKwbMOHdNVIEdxO"
    b"IGXzAWTkGsEKujQTMCQ7uuCAOW9lpAV9Hnv+4vLTZWrEDxqgEwOKAgrSD0ATR8T4dzaopJl6wmNTsgoib4ya0BV/GeLF+Xnz5OKl"
    b"OrCplxQ8HxI9I+cjnJSb74QRu3X7rk0U2WIOYfMn5rPmUnjVWmelrnZ+5PKEvLupNq8xVtlKE9VoUL58RpeUkV8MNWBxcvMggU9I"
    b"AuVjrHFUx5roWNP5Cv4iAA91cs/4fyTDZ6H8YHhIgsOgdo9SdIPtY3o6sxYJjFg39ieNHzIK8PD0/Eyyd+B+Yviplyxff8JWYIVg"
    b"DZjtvPvns0f3LCwWQhdPRwN6WLFhNoHOQuJOsyEdsU7jgFZTRH441w0ExImgXWVbDp8/6txDXc0e2UQaYfcP+5cwViItGRDZ+20c"
    b"EyWkL1jF1kA4xjii93/YrDXPGZR0pFKUtm6tbM7/Owp5Cz+BnGvN7Qhs7909ei6PENX7dMKO2Eo9b4MpkDaI6PoXX651jQRIQkbM"
    b"OMdN9haIRlMjUpkhmmuuvEJlL04BvPOA8MPsOk23Hxki9MRFXkbagwcjMg18rm4TWGAk4XrofcyEFXkM/2EJM9wWwlhXEqpzx+NK"
    b"kB49pRszzlu0YC76tmVkOaRb3WSEdHK8Jpj9VQWG8zQCi+U75Fe1XWugMJESh/Zl+H9uDLNHmpLcc22Bb4wWaohw1XwJ74XNl94n"
    b"DbVpCT7Gu66g7osUyQt2DA6HdqXGm/gbR0uwJ50LIe8kPrPvkJVNSjkhGDE1kKH9uF6B7ngrZIcSAklXoAQOAPs0+A6HN5kO7xF/"
    b"tjHhHWbXp5y4ENpjl1mwkKvAYCSr6CLPR9oJNWqJouNu9c0B216A1zs5H9iongdxxyVgUVCKGdvjU/McaXzkzJxCukh5Qi3Ukfby"
    b"z5O90HdpGQ93PXQBe4VZQEvsAJG7TbPjm9HZXzXe4RIEBFRYN1hZ0gn8YBWKpRQvSWCjCeAynQoA91ficbDo/GqiyXQUA+MOThPg"
    b"IyVokwLlKffjlIN+/zGIuS6WVONEjFfrxqMvSA1i90ciR2LLfRUBpqSELEQV+38E9hikB+NhWgnz6p1L+wASUZ0UGPPMmjH7FKtp"
    b"/Oj9wVabIKaaxoqjxo73CY7eCPJ2n1HJvYoOq48SuzRNEg6QyEwfeRJLXynvnwDk39WcyEOqTFrfOVjjBNRrPtbu4cRtmfsRBkmw"
    b"To2QJrVcu6ouVR6A0mxT9PXqt5Fz5MrVvPFhOwdp/vBpuaYzuFFTqVb7O1wV46Bd82P9/wAo1Z2803SJUozHiF9TfhjhMQLzxmNp"
    b"Nxz+WqpU3YuoJYmx0r17zHUn/iuCa/MfwyAQ632CX/YmWoNYm/BCgkKtH+u6ktBx3AZlyKDGHjBIuPshfPU0SWnUGC6/Pq9vfG6N"
    b"zjIKafKFa8COXWsr+sa72zoUqpVRPql06L5ZSsVY2/74Na3DYVl+u17dxAjGEp4ETKNyEaiyi7MNpdSjor/xbVXbMY5L9VVC7iM5"
    b"/Np6y5rBimXKi3uT/Fswh+Zcy6BHLNPw+D/9vSXvxSlVDPKN8odk8fkWO+KfJhqsQxy7XgmmueJQcgHjioaUXwS5xVQqNSLAzj3n"
    b"cNfDqfnzm/77S6cIipp5GQ7ZMUark6PJk7kNNlWxrpAcROAyCGXzR94p7AxnY9RWYNyrlHG/XoyeMsttHhC4zZQ3lB1KgZDj4H3Q"
    b"TkOFn90G6MXGD1Js3+ghSmMGNdsy+GzcbmUvpeJt1jsZWQomxLVeq/LZoWBWiD88OOc4XOlCnIKJXsOwWIJOPAjyDgmLB8XRuxnR"
    b"hgsx/vgTGk2O+/DoqKvzcoVkSd4PzRvP7TSj2DIEOkUb8BTdRyvb81wIme/VB7bqv9/m4l7P+UrMPG9j337kadeh32jYgontOCPP"
    b"znsLnh/rKcEhmp6iZ3fLL061zU63nATTJ4sycYRqc2IdFiIe9kaS6qatYmz+l4k+WTA8zJpUsYryUeEO2t2bWN5kHG2Mrmd41V2l"
    b"hIJDGOzgamw6l4rhIbg9lU3jSVJ00t7mG/5MM6W3WB0wfvE0LHpoTJJKdle2LRzlfsce4UUiszUPWEJJW82+g4+rmyzICW++O8z6"
    b"DvBTiKqpxIqGggW0g7SErBsaqY6tWxwJXTMaRVkiuR+iM3UGSQqcUfDvfI1bIX84RWjpKSuXPTMD53uCScErjpb9fli/hnbDj57G"
    b"zMyi1imCSAShBkQfTWjf4TcXM+C7x3thOmdzdY9CrHQoET8aCxuTXGinQUKGjzrbwhJB0EBvKVDaP23yH0WlkBzEQ9OcWwbwIqk2"
    b"axA1mm+cTz9L1IGThDL00yDsh36L67OBE/HJ8zGgDLJN0NcJ5zAmvqESgWRXj5Xh49ssxMySxMhzjCGNJSafuj/kevGmZBIRSjT+"
    b"cFuoZxHO0IkG/XfTlmvYDC/uVGkSCz9SXIfaXYp2ckVf0DTMRXUvfcr0WVB2X3EWwBXIpO9bn7/w9wqvAkvABDM93GKAgl+8QGXc"
    b"n1ZWIuraukHyJlvTDWfDSsrgrJf3ENNbWTOf+mQkYWgDIs3+iU7/X7D3fg27WHlxXk5kQ254EUAMW/TgoASoYa1bD+ivPyk3GNhs"
    b"TaAE+C8+RTycWcsGJnamfIdzMFnw07fy0vjUx8rvcO7flhDtdp3aU9KyIEvbFEx3ztjMVy4DO4lp9eTIzC6AAThXrStZ8xW/mAt3"
    b"mupa1KeM+H4Ze2Mm9pkOYTpuruxMbgWvYfg9TL9aSwYisnshC7gTtHfvU8W/LFiAbd5N12Qq9A0mryxlwnALaumiKjNvMotHFu7N"
    b"rpyKYByKtcAMu3HuKYFt1kOzH+0My+qqBjHjWiR/qONu+5OSS98v3nQ+jdAnefaz5KFpEucOOZ4DFdrEjaMvutxMHhw3IXk/Y2Lf"
    b"gnJ30ls6XpUWr+/krS2EEqJXPNGzsEqSldkP16jZWkhR/ACB70fSV2bRw0Jp6VBXZVghjVAX78I82+flt7DrbEVR25NU9Vs8VGYl"
    b"LRnxg8E5H1c+4MAJUxahjfAhQmLbalKB5IDqKQsOR/pKplXJk4UgI5fYVMEIuycMotslfW3QW5yxK4igMBc7nyUgIBglEvsKQt1m"
    b"zBGbz4hGml8FbpR8KcyfHC06XpwHyntTNozT0FPRfS4raZYjHDwmCH68872p1top5LGc/baupLVKYxRuOD+f60/AdIkYeNsfUuHn"
    b"qoMG4kqQrPC4YYvI+MXBb/V5RM3uY02NGSaKU3yoiPr61fwa9YLda2Lt2XYLYKFLiXbviUx/vgw4aIHBcHYJ1GcVFM+DA1omCRzp"
    b"Zjk8cHwRwnyDdbEHtEqjAj2z2ROvtms+vwEo+LDhyI7wBrxGYsTeHetLnz00qIYUOcYmP8DBvzSt+xr177zaKiRA07RyJ0bah9N5"
    b"Mp5aBzJtrHKriuoaQ7kD3z4PI1v6DpfZfv4iseeGQIgXJxCFiNBB1v0F3mf+BicN5GGGIspOiCBu8EUB8ZfG6P2jY4CyrTqiZZ9t"
    b"AIM+Mx3LHOMvYBV+DJm7OqE+qNV11uUCNWHjjcfsVvenAXsRoery5NeuFVrOjMS58CLxlalkSe5ezxlln2MRg6ODVcVpTA+Z+AVW"
    b"VZrtj/+eRGwzxYxEoMafEH+lDF2j4dHSIhh0VC8lF+3n2scPOk8U9RvAR/yBhBzTzGvuS3jbcuOG5oiYNdJmpgdH5WfZjKQ4NWsd"
    b"a++DNZFgPBk/E2ioN+352KXoRbbCFUZBpZ8Uq7Jo9Fst0PIkLuS+5hdMsPV8Cp2SB/7HO5Dr8syF65JSKEw/Mu73O4+/JVZz1Nze"
    b"uTKF9E0+Z/sYcD667IqNlbEAs73QpPR1rPkDErc0qIeBK8IzvpeDZcJc1xc/qrCfR699fjh9CuqmQzwT5T7SMRTxVeVPSZvcqH3N"
    b"ZaUWZw7RqGFQmYesTKk+HYZeg/J1H9QeP+bkfNL2rvi34MBpoGXIgFN8dVPjP/6Wt3Jq/DsAuE1AflpTepUwYFu/JL6a/Gvs8T70"
    b"Niy71yPo4fv2Stqv6CNxgJ2CYMbSA+v2ZzROrwGPE5/K7KD8R5wvGbfaqOYbfXEcvOMqm+VfMHvm+ZBZpWtltmmJCGTyCIAnpG36"
    b"0vTC6FVrE6PxzirNqAcBSvJP5Cq02OlIbNcH0sOZPSMP8Pp/xCqzqrCOwXDPSXeAfAifyXXm3WOXzs3IPUg5wE0VWA9UbIyPw4wV"
    b"9XP/OuTCZCjkD/mytdNQTSVy7R3YHEdhBq1gUAwcTy9n7srrUeXaVhGg/88Gzw74kUVJ6PncOh5DdjeR6gkPYmhqUN0qgdpGW03+"
    b"DPu3JGiHmx2lFLdrBSCdo5l5L2+Di2jRn2v0bEIGJfFH35I3syfpX20fXxEfkuhjDl63j411TaPX8AX+vaUTP/9BNKsD7I/GjsLd"
    b"Ay8RjGRc1FsAZyo3UmLs+xynAzpQSQe36dS1g+NP3nZinZjYvHsBwR9QumkP+ygLiLBRUG6JT+zTv/5ixbooGqBLV5/Y61korBax"
    b"8Ro3EkpI+Zt4dw9l4qauTCrAsPsC6ud9FPQMiP4ye6e80Juo0WsKKMvgfI6trD4Qp8nEz7yGR2dP5WQc6YM9NVIMyESqJc1kRcGv"
    b"1dsmv/YYEA43UL9JMk131Dkbja07jMvJ6SfoSISP4gk6xBatBzNAhFb2o26P6V97/qhCiE/0Tpa0LYHND0ozSDEA+weGGnw/VdsF"
    b"VJeO7MioiYVzqV1SqwaTIz5DXxEZUdNLdwlTjxLUBOHdNMOWgRitnoGItIMleQEOOYBE7w9SI+gtICLIxGQ3zbG6K35azZTFSkFt"
    b"qsX2nOfUPYAfl+HleDm+AvrVg5Fx+8WmYGC/MbUp5AgiUf5pYs/fDMFQwug9EMn6h2G+G39f30paoCJARHHfRjAX7zNy7aLaf8on"
    b"JITYTD6OemXJB+b5jKwUXR+9XK5KLblNA4ZQuWVrkcuRztFPusBy+yOClVYIN16HVkhYRJkSkGeLas1SeoYd9Pwdi9L3V0Eh1XFJ"
    b"6ttIfq+kwZrliZtT7yCBtulfHxGD3nBEsmiFDPByYed0msk/mCUUDtjk/PvT0kLsc209TpPDLJt8FdCMctDvuvlxoXA7yTk7bpeu"
    b"4xPjYVkq2y0Di+TZBt3IKjFcbruplPlXI54KVuIFOW6XFPK35S42NZ8Uf8xqI7BqGRi01kz4cioFljFlp5twJzW/PtZSQC8R1asI"
    b"/yIse8Uu5xKVcNjWhJKE9g70rB6XSNAZegUmeaq9CfNAF4B1SnOTJlheMCcZjRyf+4XA05+izhjDLi57hqw8j/NH9lw43cAcmWGv"
    b"IqxRyGxPwFmUVf9A0i3BtF2Yl6/kujeEoTqBlWUZJTb1EOwIs354NtnZyeyrxGn+hcvxnsN+jzqQtfORWJO60XPfREjHVs48hagH"
    b"8QArFDBRlQpMqUMiiYD7agiSq7dC7WaSgyfaB6AV58BbZRbPH2RnGDNbA9Q+HBFkOv65eEQuS4ycojqR0Fl+Iouu6v+JmR/pQ0yJ"
    b"aU8z3A6lTElgTzeDSmz3BJ/319g3tpg45NeOB5+/sYgSud7i4wP3OAVjKvpRatux2Ca0lGkWI1kniNN3uXZC3PEXfKZIZY98KB77"
    b"HRyRm7NhM6eX0ldvF2BKFMEQrR5sUuYNzNtIbHqzz0L25Z1+XmmslfuVCEzoCsarA8XOSV1M0ZAGng+c9sjDV4pDI+XuF2INdbhv"
    b"WuPVnrsrwQYlvojv8ZhArt5/uv5J4DhYr7oUtQ2p8cZklxNgE8tBmTgpam+nrrXc6zJaA7fNQngqAhHqDsD6iyq391EttM1e8Z3m"
    b"RPgqpaS6zsywwgDz9SZ1dxpycSnwK05yRG5pKwLxDn5M6GmSRKa95QUbuLMDh1qDXsXc5KytMs+/xiUrUa7GLL1MM1MMHlcsbLbR"
    b"RTIEH7bHSTp/flhgestNkX7wgicbhWsoWCrBma0sZs8Gh9V1u6RS8NhLf1lLmagfbB5ENyChwFodlUfy+rarnNC8HJChrH3tSWMy"
    b"2V9l3ckV1vJC2bIJevfmcivzsJEs6nvkwK6WCt1bWnLEYvrC/Dii+jh71/psAH3XW3q9Mf95RJKt/sxGmy+6F8DZ0j2f3AAslfe1"
    b"eU9bt9QeZpNgk5iRqPrphdtZtXYQrBsCE6kjxaA6pdMXp4Ik+9KyWl3A77nQNp7EffomUCHGZPVCB3UGtROLYX16Yl+F37y/uDDz"
    b"vzA/q6mzMs6WGP8BnRFo6ls6u9maLdM9/5JljIYfEzijkkkx5L+U+KKp0LWu3cqMFUxaA5TWUcN+XQ2YhDGnRImB8LplyI5xyhpL"
    b"pPURZ2DkUNZMXtKMYUuwPJgavd5aW94/MnYEHgeRWniBQeeicnjISe8BQwnmUjK0s3/4cnROBrJjBs6+PDjbqD2Hj6H2mmwUDT/H"
    b"Ftoc85DTnSv7f+NwyvKKuJc3fbuBfDq4omhifLcx0Zfei8kQQpQQ5GVgbmpvvQ2Ol/GhrIcjY+odrH7K4gTyvpujoXa9ZPpBzdiF"
    b"v6ON6/xr+XUVptZ+pUS5X5v8ZnUYi436xy+IsfA3nU1MYjdr5geEf9I40d17kmoYLWK4a6sNf55XdwkSHHjleMa3MJa+w4r4xyUg"
    b"1XHZ3Cem0Kd+NU4i9EVPcm/uU7s8R+fMxHNBQliLMRO2Qj7qboeHF75zy6rJaBdHvPx348gwOgbnR1eZ/UUS80YFrsDXNrxMnkIt"
    b"nT6FEp8tAWhQyQ7T2KDQD8IOWDkn9IMHaxRBu2IotPgwXTVc/t712RixsI6XVu/lAuVUMvc2C1mrAmy2fNWh0Au91y4mBHjfREc2"
    b"69okWwt+9Hf/4sTBXYet8RLg4CflO3UWZOITjTGTYtaQGZyyRovHLSZmE0+womnD7+zncdeqHu26KAFbcgaeywS1BzTQIgy3TBl7"
    b"pDSU3H9tbQHaDz0NE+bXsvtyAylNTSB/0C1cz0NUb6XPKbd8nywCAQvGtB4LC/LXwJOHi5+jtBFJ6IXANrvy8BLyRzw3hepG3sUb"
    b"JS7CwyWui7LGvz0/zrQK6nl7pR9aP72JrsNijVvWK+6+wrOjHo9R+5uV1Fc+8sZltVE42/4kFzt6aa9eidYVX8RCy68KBW0TL6qy"
    b"l2E6BmpHP8boQSJE5OeL+tFTqxcEpQAQt263Aj/djaNEtGpD9MblQZA1Y9ostIvkTkyqxAhXTD+YJgvzNaYTBA46pZDuJoZgd1gW"
    b"9xlpZbNTlOC3G7HdF0l9s0+csAT7hHup3uVNWtj7UEmWMHwBkIhMZFKQrAIq"
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
    if not MONGO_URI:
        logger.warning("MONGO_URI not set — running in Memory Only mode (per-bot toggles will reset on restart).")
    logger.info("Grabber Userbot started | Delay=%ss", GRAB_DELAY)
    try:
        app.run()
    finally:
        try:
            asyncio.run(_shutdown())
        except Exception:
            pass
