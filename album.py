# import webbrowser
import os, os.path
from PIL import Image
from dotenv import load_dotenv

class Album():
    def __init__(self, path):
        self.position = 0
        self.album_path = path
        self.album_size = len([name for name in os.listdir(self.album_path) if os.path.isfile(name)])
    def loadImage(self):
        fileName = os.listdir(self.album_path)[self.position]
        image = Image.open(os.path.join(self.album_path, fileName))
        print(image.format)
        #image.show()

if __name__ == "__main__":
    load_dotenv()
    album = Album('./pics')
    album.loadImage()
