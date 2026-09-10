from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
CF="/mnt/skills/examples/canvas-design/canvas-fonts/"
DJ="/usr/share/fonts/truetype/dejavu/"
FONTS={
 "Body":CF+"IBMPlexSerif-Regular.ttf", "Body-Bold":CF+"IBMPlexSerif-Bold.ttf",
 "Body-It":CF+"IBMPlexSerif-Italic.ttf", "Body-BoldIt":CF+"IBMPlexSerif-BoldItalic.ttf",
 "UI":CF+"WorkSans-Regular.ttf", "UI-Bold":CF+"WorkSans-Bold.ttf", "UI-It":CF+"WorkSans-Italic.ttf",
 "Mono":CF+"IBMPlexMono-Regular.ttf", "Mono-Bold":CF+"IBMPlexMono-Bold.ttf",
 "Marks":DJ+"DejaVuSans.ttf",
}
def register():
    for n,p in FONTS.items():
        pdfmetrics.registerFont(TTFont(n,p))
    from reportlab.pdfbase.pdfmetrics import registerFontFamily
    registerFontFamily("Body", normal="Body", bold="Body-Bold", italic="Body-It", boldItalic="Body-BoldIt")
    registerFontFamily("UI", normal="UI", bold="UI-Bold", italic="UI-It", boldItalic="UI-Bold")
    return sorted(FONTS)
