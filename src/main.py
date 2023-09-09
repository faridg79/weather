"""Import the necessary modules to build the game."""
from os import path


class GetImage:
    """This class gives us the image path by image name."""

    __main_path = path.join("assets", "images") + path.sep

    def __init__(self, image_name: str):
        """Initialize class GetImage."""
        assert isinstance(image_name, str), "addr is not str"
        self.__image_name = image_name

    @property
    def main_path(self):
        """main_path return the main path."""
        return GetImage.__main_path

    @property
    def get_image_path(self):
        """get_image_path return the image path."""
        return GetImage.__main_path + self.__image_name
