import gettext


class Mixin:
    def _(self, origin="missing"):
        aim = self.gt(origin)
        return aim

    def set_language(self):
        if self.language == "en":
            el = gettext.translation(
                "base",
                localedir="assets/locales",
                languages=["en"],
            )
        elif self.language == "de":
            el = gettext.translation(
                "base",
                localedir="assets/locales",
                languages=["de"],
            )
        el.install()
        self.gt = el.gettext
