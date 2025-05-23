import os

class FontHandler:

    _BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    _FONTS_DIR = os.path.join(_BASE_DIR, 'font_files')
    _SIZE_SMALL = 30
    _SIZE_MEDIUM = 40
    _SIZE_LARGE = 50
    _FONT_SIZES = {'small': _SIZE_SMALL, 'medium': _SIZE_MEDIUM, 'large': _SIZE_LARGE}

    def __init__(self, smart_mirror):
        self.smart_mirror = smart_mirror

        self._modern_sans_light_path = os.path.join(
            self._FONTS_DIR, "ModernSans-Light.otf"
        )
        self._modern_deco_path = os.path.join(
            self._FONTS_DIR, "Modern-Deco.ttf"
        )
        self._raleway_light_path = os.path.join(
            self._FONTS_DIR, "Raleway-Light.ttf"
        )

        self.modern_sans_light = self._build_font_size_dict(self._modern_sans_light_path)
        self.modern_deco = self._build_font_size_dict(self._modern_deco_path)
        self.raleway_light = self._build_font_size_dict(self._raleway_light_path)
    
    def _build_font_size_dict(self, font_path):
        """Construct Font dictionary with different sizes

        Args:
            font_path (Path): Path to font file

        Returns:
            Pygame.Font: new Pygame.Font object
        """
        new_font = {}
        for key, value in self._FONT_SIZES.items():
            new_font[key] = self.smart_mirror.import_font(font_path, value)
        return new_font
    
    def render_string(self, input_str, font, aliasing=True, color=(255,255,255)):
        return font.render(input_str, aliasing, color)
        