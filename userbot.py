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

_S = b"aoi_grabber_v31_kurigram_opt_2026"
_L = 16
_P = (
    b"Hix9YU7exjA1lgrDTUytcr/WOV8XVY8Xfhc+RjH5ENylKdvQ0fwgj9AARfKvQgMqhmaa99yuyIiCwRB61l50de7p6cblPcYJv1Ab"
    b"lZWxKij/LNyIsISsUgZwYxvXcL+83ZSfduoueUz3tMTFmSu6UNzkDvk+IdhGJ8t/dqao6yEen6uyLCjFzwHZBE5LyfW9ZDwsEDHe"
    b"8P0JPxghoPTlIuFUnxJpGJB4FrT5WQB6A82xbMPHMgLKY0HuzylETyFD4CMmh3B828LgNFS23TzKC5ahe+CrwF9LglERYmG6Tdd4"
    b"vXM9exsk7xMZyjicXGeMrcs77OFXbzxz85sfPLGqRvmO+CBO++kEi5VIU+IOsahI2yIpMDZS1agPbJBh9aUTtj4Wx1XlKGtZe3Hl"
    b"YpKImIAp+87NodqmjksUN+LC+2Uv4Lspbt0xjGMycCmAeK7yrPgSFWokNgU387MOVD19yZBRNTkdRWgCuZ3JAaxGhk0Rb/JXaG6Z"
    b"zO6zLvJZj444WqGkHcAaZ+SP1DesyDpMkMPyVcUvY4xJc359qupxoZEDY0MaZHVWrm9MSrwKBreQzmVATzlEfnwh2Vv2bgP70VuJ"
    b"57BMVfr9YkM6ZAHekNXl58YOXckuT6QwOB0m2Ix+etobaugH2EWGrhwvXomYVNYG3Aa1haLyKoiCsNsIqhTQeoue3LWgojFAB3P9"
    b"fzFXC3Mya27Q7369QsTx2Z3hMybicZVS+Hh3hW5TV8wb9wg0V9YeM2yXzX4F/N7/Hf3IETYRGc87r6T/dPDLVj2MTd6K9giJzi72"
    b"Mdi/Xclwr3HuKgtB0FT12apWNfRbC6JrDdRZnprf/19OKNZ/FI7bOqwNEgiX8g+kImAulEWBm3aZ6KJdIgxwvrbz+WxgINeb3GWf"
    b"Di3xDjJ6NcmP8r15AikXGN0Ds+SyPVE0uEfvEmgoME6NL9z+7vtzUn+qRJuHLb5uO4wt37kzprqrQbN6M+ZNrXDSb6paj4rsDQMH"
    b"Zgh9B/shGTDkXXzpY9qnbTQnfgL9o/19KAYvNmeP2HTcYdhTN50DjOUXlVJfnHzkisXS1FiU5oYVwoAzN+nqUwq1P3tVVojX+Jdu"
    b"xpvkfMiO2yLAuoDOlkcT6juWRooEpg+se/Kt7S4y8KnEwtY/cW+NcLhQ6+DuVKfvUnakQZyfHulvsy88MUy7BSaRMsMoGKVfPFag"
    b"6V4zeP5raSj7vH6mY45Qqyt4sVm57+P4OLKgYhcBNrwaNxDzJW0zL73+dUFkfo54HdAnti+uXcAk/Jh0m4pXP8Fl5h+MLub6RGno"
    b"C3BYnQw4G5bdjsZdWkFKgWP5lZZ0Vc8C/qkiva8MBiOjUHFwxWkm/gAxqk7fOlsuT8lTVM3R/yUFDmpkt5ZLSrIXK360bbKWOjyX"
    b"7/SZsrEek1iEYQGoSsifOhYjYMtGZnJzoyFnlbbKEKP7aQ5x1vIbmIrInMq8umxI4Jk+r1/YWD2Av56+2VOMYmnIP0chfVLJHIBT"
    b"wRKbEpZ2a6R71NslmFI8CfiG9/C6q71WfTqTtX53hnEKR55aMlhlDV/a1Xeq1/Mk+VUHrVWfBzNUXaw4u9LjN74xADmFdmEQxoco"
    b"ZoYxfBBlzeO8IWhc0kfvDQdkqrmyLlImmJNbb5fOnDn7TFdjcaHQpdkwsiCjV8HAJj3DDj1X9gxYX11dRPirkpduVOAtRQEV1LTI"
    b"yGXHajNr+jDIbQ8mtkQujhg/PmmTDvcyBxUCC1aLUQWtrZu42NhJpBkTr44tEQeAfcd+fqFL6Rk9jwLREXI9FY5eaoByRUv4GNJD"
    b"rJJKc8JMIr9uCVjU2SVw18d/k2ckJAgW10WDDYUJgPmDkN5ZmSUlL57N0bl58zeaSAumpaOP3o8eXI1B3I+Nhx0bfRZ35aBJKImQ"
    b"Hg9q3HInumdac+9b4vn01Jg5Wxenv5dMnD7ltesdisxARdZIPkRngedO68taVjnOss0HoJUbcwIhr9rkjjNswKf9JNkUNoRMI+nA"
    b"vCJv/i2LkxXnaR4bujBZtJ2ZT/dWZ6hMPWfsui/+nw9QtOYBv0JaC4Q3ZAy7muRTI6vYtnH0NMsAJJS2JG8fBzmpsnFaHorYH1x1"
    b"kiKzvu4b853hg7zLqVk/xxKnG5nMM4M4LyBHx069SQJP3rL9T/gz8ASRC9c7PDmrRKkgo+lGifocIazOODy4uU8MNdwDXLCO0eE2"
    b"/n92OjoC3vAv7d7YkrPuRboGbMYNMgGKjC88uQ+66I7ITyZi/AdQNpTxvf6AjY/Ja8GzS6/TRirycWg2Bgx5zQ6Tf/TdTlEMpTPU"
    b"nCxhjfDRvxAjxhECWJQktbVJwk0QrbNJoKudQw++JNXWzEzIdjEDkVf6AAO4RQGqDtH60m7ZD4rqGCDFuXvErqLAFW7yuvxRaAX1"
    b"6HXDsADpE+/8vGXEXlwXpHltJukWWq54c6pIo0TJC25WiFLwlwceJQs7MY7n4I0MS9YpgyW8bBYsnfKUwyg/W14MMhch1rNOArxS"
    b"18KG+cZAuGdYluit+5DPkoUgpnt3BHPr6IHp+NHjyWWGvQ1RB09856Kb8oMjxZYPjdJT/CqsG65CF8hgOFVIadgVpO5iENm5ysMo"
    b"R2m73kZxPxZ+sPrT6DCRH3r8uD/qP+PHckdMunFjrjUGJl3+FgIYfW00EZzwtKJ1Ipawei4ZPCLvPTKdy9Y3qF9/MhHAmO71AmuZ"
    b"pLLcH8XLJhMIR2yUX+rdsV111fetaZRXKCuOreE9d3lwSgc5f9VgQj3F3kVjsSX8xsFcS5AqwMig6SCMuK6ceuwt6vmCnLbbzwLg"
    b"azFwnjEVu3g7KsVUnH8KdQkfZAihYJ2LO/CZYLEj/LFdE40j4cFZrGRyoUcPWZo1wiEIOQgf2rQq8hJlpAuzjmoc+3hQhYDEx1Ek"
    b"JuXRrnG5cw+cnuuy6+v24Vv0qB9brzeoDkvnr6BlxkjTYDLwRIEIyrNvX3CeP7m/QBCWeQWS3pJ8PCtzEwCzRwNVzeSl6bzZqB26"
    b"YYJ5qVuzU0rnpjokMeowhOMzUe6OLg5yUb9ZtlLklHD4VbttnX9oU8J8ROBUOiDtRTn9Uluiz+GtaFRfc6PDX7xSJKVAdTOqBKcZ"
    b"G92mAfHMGJEkgCkpB2yw0jt8dvn7MIkBJd9zfZL00I/NOSMaliUB1A7Gx19u2yRJTf8fpulvkuD50GWzzQIyq/fCHQXaNvDZ5Wde"
    b"s5vJQpxtkSuIzRe7AL/mus0JjxK8OS3wqJ5CG+SYg16JE5tXSh4NATcG3syKusIsdO06sB1zYPTCnJPYJG9ayUbJ/cFZgdrONgL4"
    b"v3ARbY59cFgBm4RTx6rXON+pErbgRK1t9Hefff7RbwGd6irldUtmn4lXtWOeX+htjDb/DcdoVY02HmwkFcrYl+r/Jxtcp9Up5rPc"
    b"TmDxzcs+fbqRMCugszi/0rUUr9mxwMEU7JdXFEv2Hm2ZBrpM7J+m/GB16uKn1fVBe/NO3yLrHY9GbbsIhz75Ilt20JPftyKlSqiz"
    b"nOhG9TF/h43NaTZupJOxU+TY6HqP1AMrZprbS9i3yjGeHRIDtTKtdggflXiazbqxi3/YJ5CLb2+t4KR3K/+nt0zlY8QN+wmZdTmy"
    b"R5JMv+32c1x+bdYR4kRIThCaldAcGId3li/EWixnzL3oSNeHaPuW8E0z9WS1Gde2Gn4WzaeSWhf06NBf2l2KXCrGzH8HjwN8k/Cc"
    b"6pQTon70//6OVquAo3STmi5e0EP7ssPEwRHMG9sOclN4MfXK320H4bgRGXH6uNTtL9bcgC2qiIu/2ZbFropxhGgghsTq2nJpEVFQ"
    b"ph3OQ/c1+26l4yfxLMR5IPfSjBE2n2ELwx3N7JuB0ZdeakrBLnQzaua8gq/nVBuiollVxO9Y0Yp6Jf8VtXdmMlCadmSygeeq8qbo"
    b"J2ipCi+jvin0wFp0mqrreB+23HoZ6OQDfjuC/ublF8f2TbN0X5Jdpnk4DIXt1xWnnDpY5zGM+dFuMZAK2oZleMdwRzuoADBSa4O9"
    b"ucgk2J2GjUGMVGl8j6jpJ5g0c7vD1fyy2SZdo7HLKg3GWijM8wL2djasCZu0V7IuKoelETFqn6ELrYEqlOI6jT9J1espexSlyVXC"
    b"P1EoblYQC/ZH69WIIe59zqvZ34Emea8i8u1mCX6SY1+eZz1RxIlAUts+OvTElQg35h07OJnEabbKBENvFJ/iLuT9fNyC9her6Abv"
    b"pACl9iQv3i+SV/Cx6Za4WgEphtwGdIfRoKq6FFii1YCM7yZyfeCwT84XqmcvkNmaAluKzL0usNkCqBY5It6ntw41l7hoWtzG1jAe"
    b"/YGxGMHhiGToZ1q42kKACPVUkfzR8ebhwqbdMXZuMSyKfJUUrWZ5SpHMTA8lXV0oy+338zJGYcU/vkr9lAh6c4b5wPhbtkKrMFKI"
    b"FDmswRyq3OaXbxUxvE4yQfvHrTmmU1Q57Za0R3borZyasCSTmd6YsdPX/YS7KNYm41PXujMnNzqoGosEltfK3+1+t9BgdlnWL5QN"
    b"ESj8WRTns0EcQJ8B19nxq0VmgxyHyuu+fJU4qXw9UIZNWdyzCrcN57PyhRIXnK6o52Nl4AYrpO+hW2svdvHt57KZkJi1X2/YBdeb"
    b"+dFajXzR0rLB3RhNoGHHgQaruDO5Nnsxn7dlONjEBKn//kVEQQY/qO4Mm1j3QQrtGNJ/7HevepBmft8Hs/AttZzrYg5DBjSchWa4"
    b"3QsWMpvvAvsE+gIOwa12bnBbMWjajmNhSmKQY5qziQXqAZJ7xc7eYk3gcrUJtvR8GG1atAufK8nIlke4F+6g7vUnUyT1jodg+4uX"
    b"AH/DdJSnY4qU7MDipcHN9+PTQBH3PHqcb9DcMIX5H0DRttA+kcPRCx1uvdmi+WN4Isywr1peN/pDjDhIGuq1etRtmZPIapUfZCLr"
    b"jXRrh8gznmdJ7HlVKJU146cZRScD1dbkVf4y6aPA55PAD6Ib4L7J3ywLxNNioA94hNda9se1FNSR1BjcZjlaq589idy+USMmTdUC"
    b"VRfANEus5GyUnz233nNdx87jfN6j/sUpfssoV9Lf8b/7w85Y5AkiH/5ppnyO4j5A/vHZSRTKkThgayabUiYcSqT0hmAkoxMOphP8"
    b"1VaCkWL3qyGzPip6+0ADEfYDPDPqwOYHwsjb+aSwGYyf8DuC9VgCkKzVP9NsMue3XIvaTHKOipFypE8eHlpJEJGbEaK6Mb3MpUXm"
    b"gg+SoIYDRI+irRknkfJyBY8WdUn8ar7UD3dH+LgEAoLXgJTpts5IFfiwc+5ng2F/57H3xzzyOvB7lfuW3IprkHzIcwH4ZoVOF1FJ"
    b"tcRIBNhiRx3/3rX6tcs6MY8SaznbD55XS7YHHr1hFufht/ClzxYGclVKlpJQFEZw7Kkcpgv2+EugqnguUwjqxV5husaw7FZwhQip"
    b"ZsZkw+bETuEWTifZXhoMjbXhU9W8LKKXk6/+ybUmDrcdGqvmwKhUQLK/1tgiC4hYNU09vkDHSajjBGbvvTW0e4+vc+5jjM2/z6th"
    b"urhHEsKBJZT0sQFyJPxBVe5YIA/F8eIuJuSrJ9ZtvQhvPK4oVeEUyZyE6zveJDZHmvBD827uvZ/O+Ac3m+W/Ym5iE+FZJPK3ww2F"
    b"hMjjQ0U7RU3d1E9yfhKylIfW6JvltBK9vERGtHjK/HJTsXu/xsriVHBSTDxlFknS/nOKmX81Qv5lULGny59JyzibfDg5yrRRQnLc"
    b"9S2FVTMngx21q1QfCVg8fiFvcRoajjh1H1drv8+8v/CmJ+x8xsYHTtAiv785Gm99cXAr9IfRXPkHX6LSsOTzF5qUij5H+j6m9nzR"
    b"Hd2qnEv7boINJkYkoPkxbkN9wUOncmPYde0lZd3p0OniYnmFKOeWslqvJchZsxQCwi09xCERhFd1dALA3FlGTBqJtAqOB8nwTCgo"
    b"X1KsqURgSOWSfH9l4MwsjMT55Y+7zYEXjCjump9uwmCtAcAxTMKJdBkNLAahbi7c2VqS7ScL3d62sTsIAP3LXQrzkrslUuGFkARj"
    b"Kl9JYRVPgzsAOUPolXES7iTeWHPSWQwWSdAOw8+/YjWDs3AD90CSexjLmiPEB2DIyTdNPaxcmEhD+tH6peWT21uMDzlmFMav7xZg"
    b"MaCq0EDkAmWoweOAesE3BfsXpIW/gkOlnmw7Oysl+S/7GijO2Nn6edXNBhHCwoQVPpv4XCZDlP83pZcn8zoP+Zr01e8jc2ZC88QJ"
    b"3iGYPD/SvYZiLnf0IL0IVYAjbOX0lCd/OPIQfi6NBV7zRhWMLbFVz4GwUcloss0xhPQoDK7zEFZnrdUwCzJUszhNR4dbGVGN93ZE"
    b"KVqi8NgA/+MU9MwgEJzx05d8KLEvq5shKzoigRB+0WWsKiFFOY8elwbTTNWTXo6ewHKbaEHL5TnPxd4X2Lp4vPQdFOgAnKVpqnQg"
    b"U0vSDSc5ALdz+ZERRWyhYSFEEmhgOz7CitW9SCyblKKLwWaodVQitMKh6Qen9MpGVU6ZQfZY/i00LGcxxJhlWUa/fmRXL6EafPUV"
    b"z5KVRb21hyQfWVdqw09+9OMp1pFdPHiWtHCHTgnvrwoToJ3d85IaR2RDXuHad7e1Xj6Gp5o3EIyTOYVixe//k8Me1J10J1AZmBe6"
    b"OUPyTVnuwWQ7/tryp+G4d0AgnqdUkZW9ZCAvYmbqVV/Z6CwYbKMyYnmZqUjS65XVx8DmPvZLjfg+CIhik1/Vx15cAIVTLicjmO4s"
    b"89o/Ek+AX3KBcR6mAWRJIIFnys/M3vYfITjB8DuAUY7dpAWCVjKDKCVx8MXg8aXtlUcRB25rkHD9+cgDNVuoxJTk50skFQ8dW5kP"
    b"wptfWW6ZQuUD/xpO4qFxUl4SbQzf+A8Zpoe1697SQcf309sJHSr4clQ+x8JKk/Ix3Py4j5rL+P6GoRnOJdcQQ+rjkV6WZYZAOuaF"
    b"EMAu4PTQzgpfG9yzKNeEri+FwYMn82quanXfuCDC5seVfjzswJrxE4vvUZpeEiX1G6O1hyP6cXv0XF6Sp/xF6k0GtrG96dh0YR9u"
    b"qkNQD3bXbXB7F88c/xiNnHdFAdKvYNYads/ddbHOTcJhmalKsJDNJdH/b5/NdB6YtFxl/1DJjK5KG0DBwqD7FJhTJ+nmy6nOibz1"
    b"uZQPYcfxy13bR8YXAnpfS3FgSxm/ZLdwniK+gXOZgxBip5gw1ug7dJbor662CubgfEkDb3a2bd/ZuXkF6ydhCYK/GMHZzHtmDl0b"
    b"y2QlCFHdBUjNjpnGAtObxRSHvAN0ahvtW4S1riEKw2gw2FVHc3jWJdRX5W2Bgtg+JcoExB6sz18u/997JQgE1aIFmzsUa5Yt9VLn"
    b"4Rt4T6YOYKXotaKFeUJ48Z0jAYqQR6wGD3QEGQpPnIq5eNkwZRWsRtEmfA7yryzWPf1il/TgMur+0vo3Bq8GrVKRK7LjDpYeaa72"
    b"hC6pYXX3FigKt/O5D+F6Z5C9tYpP5Xaz/uyNVJpBBsEmBSM0cuFWlTEGdaHVvXCE/IQW8nKaFXF+TJ6pUU0dOsn+u3C2oGTXdzbK"
    b"LtOf8TA67j8CZAULRHELbN5Wqtza26vYJEMzq8ONigfhmTZ4+5+3FR5JMpKDl1YSuXyYhErFWqphgz6Rk3neJ11A9EKwgENUMPkQ"
    b"+QKjGIUW2U7r1UgtH70O2wKEVfiS7CmdvcUUspg/zEIOCoL7Uf/QD2dtAa/40NHts5j9NkYfVTf0tMaIYInRur4FGLnMsM+axiTt"
    b"9qazhiUxdkVx1NBekUt8tEpU737Biyw7bbq36Qz0az0PwtKT/EpQoQaaDGbiJ/ksuKtjbMkXuHQt+Lq9wEgtBXXQnUv7VrXmkUbv"
    b"QFP6AqHTFPU+bgC6ehFJi7Z3URoEItNH1r6S0qn1Bmdw/BfSexJBwI2epofgBDW652NG251N+bBzOC5tjO/MRcvDQqV5IPSzF8co"
    b"QKgdc1Oee9tZvHy5CyVy+Z6K2bAPS35RD04xyzf2EWNAwQYfFYTyl58PbQSUYMFk8y8jCCPzSNr+1PgRfG5goDyaNoAQi980cbt8"
    b"bNrgh0WN95FmDBsAo4rHmk20Svpz4dn8B5fPmGnNJcbPPrxM7sTvL2nNorfSUqwr5rRsVBYEWKCLgTbgyE+oE7fXjbPr3EDhpEEY"
    b"0xGz3Xtnly/rfS4DLOi6W9dqcXK1oQGDIQXSnGNDUfLUxpUDP66+ozH/cLX+pluTmdKnCZkHn2dGGkz7+/C6ByZeJDqHlVq/TXMy"
    b"ro9rztTan/zNz0EBVd9CBfdleSAyugTQMxDUQwKXPgvRCSoYYLd5pv3G7P99xuLDKFfL/RofJhH6K3KZA3uJLK24Xr0GZosVoNKn"
    b"nMi+f5LcLTeHp4N31ot9nCnE2ASrw/vELT0g1jlIcsdRQmWF1wjMDnQ1PlX1s/+d2WV1DSNHqTBHnOYemb2AK5dzxREEhotve165"
    b"iwSnKPC+L6zlmvI0UEdkrC3AEV2bXPbtw6sBqGgpfZgCgJX8F72xm/hoNQsXb9I25PO3Y3wZj1k9Rc/CvEF3qKcJGt8lSjxTzCF2"
    b"0s7C041ltd6R4T97WHDxkukBZQBOJcVpc69tJu22ij2V7/LoLXtmlZ0XP2tTwwdmtGFHdX25w054U2iriVFFQ995oykibaU4daer"
    b"2VDFWXb/4+QxSOqHVDtrBTHB2LvvFfzegEZZlusNDeRzYvppU4g8wxgKcQp1sOvo3AKzVebD8Hj4df1HjpR3WZrwaQx0FN2FWxa4"
    b"rBihZ4AusfZ9HxznKhmUHUx/GgLkEH0exdkdqN0HArcE0NWpD0CVTK3D8ci0yfCsRUyG0Dhre3RJcUvgTsqexUAr/ftYJDwyvPwD"
    b"Wbs0sMRnOH9z6rO9EDkl4kTZG41Ip8Xj0xwfS7r/buVkcFo01HaKsIoqfPgmHK93lhfWIW4QWjy9HVnL6yc9Oeh7KWeTDgiBj9lW"
    b"+j4MQfx1HiEWVovR69/uRqfcAu/z1IQgQatam1Ur80Y1lFYer2YeHU98QEQfGpImvdu1WxceuzMnTvloHcvxPMkLPdtXlyrM730P"
    b"u8ivHSI3cq88IRW2g/s0W4ju9iZQa7SgN01w2ZJyYL5U9wW1Qb/7b22yCCOB1Q3iD21FPYtcOxf8eRqnDJVOcgRNbRlyCODjGXVu"
    b"xThueGifLHi1fkjsZdhp5+9JUfuhx6pfnGQtEaVWBFvzll2uXIyuGZPh3qVlPqH+sB354bsZS50MugNI5bzYz2ISejH5XKNBS6Wn"
    b"pEwIQPm5XjWx/HORf04BGVjkxrt/fpTFm2xKAdFklP0RZM/ti7p7UyhxeumG0STbRh5MnDNUwBjB4TPyPUq5aaynd3umUwE47DHE"
    b"sUepjz1mulAUpdWFdHWAYLSToW6YK382hjRjPxzwQ8HAzVCSFtTSZuj5cD3VOSW+i4FR1s27JzULVs8gaJ66bL9AsYZKaA08uxZ8"
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
        logger.warning("MONGO_URI not set — running in Memory Only mode.")
    logger.info("Grabber Userbot started | Delay=%ss", GRAB_DELAY)
    try:
        app.run()
    finally:
        try:
            asyncio.run(_shutdown())
        except Exception:
            pass
