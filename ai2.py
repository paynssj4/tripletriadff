from PIL import Image, ImageDraw, ImageFont
import os

class Card:
    def __init__(self, name: str, attribute: str, numbers: list, image: str):
        self.name = name
        self.attribute = attribute
        self.numbers = numbers
        self.image = os.path.join('Img', image)  # Utiliser le nouveau dossier "Img"

    def __hash__(self):
        return hash((self.name, self.attribute, tuple(self.numbers)))

    def __str__(self):
        return f"{self.name}: {self.attribute} - {self.numbers}"

    def to_dict(self):
        return {
            'name': self.name,
            'attribute': self.attribute,
            'numbers': self.numbers,
            'image': self.image
        }

   