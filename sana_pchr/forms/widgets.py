from django.forms.widgets import Widget
from django.utils.safestring import SafeString
from io import BytesIO
import qrcode
import qrcode.image.svg


class QRWidget(Widget):
    def render(self, name, value, attrs=None):
        svg_img = qrcode.make(value, image_factory=qrcode.image.svg.SvgPathImage)
        # We write out a valid SVG document
        svg_raw = BytesIO()
        svg_img.save(svg_raw)
        # Then, take advantage of modern browsers' support for inline <svg> images
        return SafeString(svg_raw.getvalue().decode("ascii"))
