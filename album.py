# import webbrowser
import os, os.path
from PIL import Image
from dotenv import load_dotenv

class Album():
    def __init__(self, path):
        self.position = 0
        self.album_path = path
        self.album_size = len([name for name in os.listdir(self.album_path) if os.path.isfile(os.path.join(self.album_path,name))])
    def loadImage(self):
        current_album_files = [name for name in os.listdir(self.album_path) if os.path.isfile(os.path.join(self.album_path,name))]
        fileName = current_album_files[self.position]
        image = Image.open(os.path.join(self.album_path, fileName))
        # Resize the image for display
        image = image.resize((640, 480))
        print(image.format)
        image.show()

if __name__ == "__main__":
    load_dotenv()
    album = Album(os.getenv('BASE_PIC_PATH'))
    album.loadImage()
