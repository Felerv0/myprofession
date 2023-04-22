from consts.strings import DOMAIN
import qrcode


def get_secret_key():
    return open("consts/key.txt").readlines()[0].rstrip("\n")


def make_qr(src):
    img = qrcode.make(f"{DOMAIN}/project/{src}")
    s = f"static/tmp/{src}.png"
    img.save(s)
    return s