import os
import textwrap
from pathlib import Path
from typing import TYPE_CHECKING, Any

from PIL import Image, ImageDraw, ImageFont, ImageOps

from settings.models import settings

if TYPE_CHECKING:
    from django.db.models.fields.files import ImageFieldFile

    from bd_models.models import BallInstance


SOURCES_PATH = Path(os.path.dirname(os.path.abspath(__file__)), "./src")
WIDTH = 1500
HEIGHT = 2000

RECTANGLE_WIDTH = WIDTH - 40
RECTANGLE_HEIGHT = (HEIGHT // 5) * 2

CORNERS = ((34, 261), (1393, 992))
artwork_size = [b - a for a, b in zip(*CORNERS)]

LEFT_MARGIN = 60
RIGHT_MARGIN = WIDTH - 60

title_font = ImageFont.truetype(str(SOURCES_PATH / "ArsenicaTrial-Extrabold.ttf"), 170)
capacity_name_font = ImageFont.truetype(str(SOURCES_PATH / "Bobby Jones Soft.otf"), 110)
capacity_description_font = ImageFont.truetype(str(SOURCES_PATH / "OpenSans-Semibold.ttf"), 75)
stats_font = ImageFont.truetype(str(SOURCES_PATH / "Bobby Jones Soft.otf"), 130)
credits_font = ImageFont.truetype(str(SOURCES_PATH / "arial.ttf"), 40)

credits_color_cache = {}


def open_image(image_file: "ImageFieldFile") -> Image.Image:
    return Image.open(image_file.path).convert("RGBA")


def get_credit_color(image: Image.Image, region: tuple) -> tuple:
    image = image.crop(region)
    brightness = sum(image.convert("L").getdata()) / image.width / image.height  # type: ignore
    return (0, 0, 0, 255) if brightness > 100 else (255, 255, 255, 255)


def draw_card(ball_instance: "BallInstance") -> tuple[Image.Image, dict[str, Any]]:
    ball = ball_instance.countryball
    ball_health = (237, 115, 101, 255)
    ball_credits = ball.credits
    special_credits = ""
    card_name = ball.cached_regime.name
    if special_image := ball_instance.special_card:
        card_name = getattr(ball_instance.specialcard, "name", card_name)
        image = open_image(special_image)
        if ball_instance.specialcard and ball_instance.specialcard.credits:
            special_credits += f" • Special Author: {ball_instance.specialcard.credits}"
    else:
        image = open_image(ball.cached_regime.background)
    icon = open_image(ball.cached_economy.icon) if ball.cached_economy else None

    draw = ImageDraw.Draw(image)
    
    # Name (Left) and Rarity (Right, moved slightly inward)
    draw.text((LEFT_MARGIN, 20), ball.short_name or ball.country, font=title_font, stroke_width=2, stroke_fill=(0, 0, 0, 255))
    draw.text(
        (RIGHT_MARGIN - 40, 20),
        str(ball.rarity),
        font=title_font,
        anchor="ra",
        stroke_width=2,
        stroke_fill=(0, 0, 0, 255),
    )

    icon_width = 150
    if icon:
        icon = ImageOps.fit(icon, (icon_width, icon_width))
    
    content_y = 1050

    cap_name = textwrap.wrap(f"AKA: {ball.capacity_name}", width=26)
    for i, line in enumerate(cap_name):
        draw.text(
            (LEFT_MARGIN, content_y + (85 * i)),
            line,
            font=capacity_name_font,
            fill=(230, 230, 230, 255),
            stroke_width=2,
            stroke_fill=(0, 0, 0, 255),
        )

    # Economy icon moved slightly more to the left
    if icon:
        image.paste(icon, (RIGHT_MARGIN - icon_width - 40, content_y), mask=icon)
        icon.close()

    capacity_description_lines = (
        wrapped_line
        for newline in ball.capacity_description.splitlines()
        for wrapped_line in textwrap.wrap(newline, 32)
    )

    desc_y_start = content_y + (100 * len(cap_name)) + 20
    for i, line in enumerate(capacity_description_lines):
        draw.text(
            (LEFT_MARGIN, desc_y_start + 80 * i),
            line,
            font=capacity_description_font,
            stroke_width=1,
            stroke_fill=(0, 0, 0, 255),
        )

    # Stats layout: Health centered right before the heart icon, Attack right after
    # Heart center is around X = 750 (Width / 2)
    draw.text(
        (960, 1820),
        str(ball_instance.health),
        font=stats_font,
        fill=ball_health,
        stroke_width=1,
        stroke_fill=(0, 0, 0, 255),
        anchor="ra",
    )
    draw.text(
        (1200, 1820),
        str(ball_instance.attack),
        font=stats_font,
        fill=(252, 194, 76, 255),
        stroke_width=1,
        stroke_fill=(0, 0, 0, 255),
    )

    if card_name in credits_color_cache:
        credits_color = credits_color_cache[card_name]
    else:
        credits_color = get_credit_color(image, (0, int(image.height * 0.8), image.width, image.height))
        credits_color_cache[card_name] = credits_color
    draw.text(
            (33, 1870),
            f"Created by El Laggron\nOwners: @whogivesafuck, @Sonex\n Dev & Co-Owner: @imts3747, @azmir, @Trev",
            font=credits_font,
            fill=credits_color,
            stroke_width=0,
            stroke_fill=(255, 255, 255, 255),
        )

    artwork = open_image(ball.collection_card)
    image.paste(ImageOps.fit(artwork, artwork_size), CORNERS[0])  # type: ignore
    artwork.close()

    return image, {"format": "WEBP"}