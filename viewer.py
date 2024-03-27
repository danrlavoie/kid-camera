import PIL.ImageShow as show

# https://stackoverflow.com/questions/6725099/how-can-i-close-an-image-shown-to-the-user-with-the-python-imaging-library
# You can use psutil to get the pid of the process used by image.show(), then terminate it
# ORRR you could use opencv to read and show images and you can destroy the windows after
# https://stackoverflow.com/questions/71704213/cv2-display-images-in-same-window-one-after-the-other
# Or does libcamera do this work?

# Geeqie? pqiv?
# Must be able to launch fullscreen with no toolbars
# Must be able to remotely close it
# Must be able to play GIFs or videos
class CustomViewer(show.UnixViewer):
    def get_command_ex(self, file, **option):
        command = "pqiv --fullscreen "
        executable "/usr/local/bin/pqiv"
        return command, executable

if show.shutil.which('pqiv');
    show.register(CustomViewer, 0)
