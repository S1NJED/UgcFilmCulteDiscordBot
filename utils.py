import sqlite3
import requests
from PIL import Image
from io import BytesIO
import os

def connDb():
    return sqlite3.connect(os.getenv("DB_NAME"))

# merci chat gpt mdr 
def calcul_avg_color(imageUrl):
    req = requests.get(imageUrl)
    bytes = BytesIO(req.content)
    img = Image.open(bytes)

    img = img.convert("RGB")

    # Initialize variables to store the sum of colors
    total_red = 0
    total_green = 0
    total_blue = 0
    pixel_count = 0

    # Loop through each pixel in the image
    for pixel in img.getdata():
        r, g, b = pixel
        total_red += r
        total_green += g
        total_blue += b
        pixel_count += 1

    # Calculate the average color
    average_red = total_red // pixel_count
    average_green = total_green // pixel_count
    average_blue = total_blue // pixel_count

    return (average_red, average_green, average_blue)

MONTHS = [
    "Janvier",
    "Février",
    "Mars",
    "Avril",
    "Mai",
    "Juin",
    "Juillet",
    "Aout",
    "Septembre",
    "Octobre",
    "Novembre",
    "Décembre",
]

DAYS = [
    "Lundi",
    "Mardi",
    "Mercredi",
    "Jeudi",
    "Vendredi",
    "Samedi",
    "Dimanche",
]
