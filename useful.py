from consts.strings import DOMAIN
import qrcode


def get_secret_key():
    try:
        return open("consts/key.txt").readlines()[0].rstrip("\n")
    except Exception as e:
        raise ValueError("No secret key file in consts/key.txt")


def make_qr(src):
    img = qrcode.make(f"{DOMAIN}/project/{src}")
    s = f"static/tmp/{src}.png"
    img.save(s)
    return s