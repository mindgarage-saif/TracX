import gettext


class Mixin:
    def _(self, origin="missing"):
        return self.gt(origin)

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
