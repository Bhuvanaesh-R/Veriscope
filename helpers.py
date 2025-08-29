import requests

from flask import redirect, render_template, session
from functools import wraps
from PIL import Image, ImageDraw, ImageFont
import os


def genserver(id):
    r = requests.post(f"https://discord.com/api/v10/guilds/{id}/channels" \
        f"?name={0}" \
        f"&type=0")
    
    print(r)
        


def genimage(top, bottom):
    image_width = 2880
    image_height = 1800
    background_img = "static/imgs/classroom_board.jpg"
    text_color = (255, 255, 255)

    img = Image.open(background_img).convert("RGBA")
    img = img.resize((image_width, image_height))

    overlay = Image.new("RGBA", img.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)

    try:
        top_font = ImageFont.truetype("arial.ttf", 200)
        bottom_font = ImageFont.truetype("arial.ttf", 160)
    except:
        top_font = ImageFont.truetype("DejaVuSans.ttf", 200)
        bottom_font = ImageFont.truetype("DejaVuSans.ttf", 160)


    top_text_size = draw.textbbox((0, 0), top, font=top_font)
    top_x = (image_width - (top_text_size[2] - top_text_size[0])) // 2
    top_y = image_height // 3 - 100

    bottom_text_size = draw.textbbox((0, 0), bottom, font=bottom_font)
    bottom_x = (image_width - (bottom_text_size[2] - bottom_text_size[0])) // 2
    bottom_y = image_height * 2 // 3

    rectangle_margin = 60
    transparent_black = (0, 0, 0, 0)

    draw.rectangle(
        [(top_x - rectangle_margin, top_y - 40),
         (top_x + top_text_size[2] - top_text_size[0] + rectangle_margin, top_y + 120)],
        fill=transparent_black
    )

    draw.rectangle(
        [(bottom_x - rectangle_margin, bottom_y - 40),
         (bottom_x + bottom_text_size[2] - bottom_text_size[0] + rectangle_margin, bottom_y + 100)],
        fill=transparent_black
    )

    draw.text((top_x, top_y), top, font=top_font, fill=text_color)
    draw.text((bottom_x, bottom_y), bottom, font=bottom_font, fill=text_color)

    final_image = Image.alpha_composite(img, overlay)

    output_path = f"static/generated/{top}_{bottom}.png"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    final_image.save(output_path)

    return output_path


def apology(message, code=400):
    """Render message as an apology to user."""

    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [
            ("-", "--"),
            (" ", "-"),
            ("_", "__"),
            ("?", "~q"),
            ("%", "~p"),
            ("#", "~h"),
            ("/", "~s"),
            ('"', "''"),
        ]:
            s = s.replace(old, new)
        return s
    
    genimage(f"{code}", escape(message))
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function



if __name__ == "__main__":
    genserver(1390665340186398740)