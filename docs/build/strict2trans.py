"""Convert an ISO-Strict OOXML package to Transitional in place.

The IEEE template ships with purl.oclc.org/ooxml namespaces and pt-suffixed
measurements, which Word reads but LibreOffice refuses. Rewriting to the
transitional namespaces and twips keeps the file Word-compatible and makes it
renderable, so the output can actually be inspected.
"""
import pathlib, re, sys

root = pathlib.Path(sys.argv[1])

NS = {
    "http://purl.oclc.org/ooxml/wordprocessingml/main":
        "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "http://purl.oclc.org/ooxml/officeDocument/relationships":
        "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "http://purl.oclc.org/ooxml/officeDocument/math":
        "http://schemas.openxmlformats.org/officeDocument/2006/math",
    "http://purl.oclc.org/ooxml/drawingml/wordprocessingDrawing":
        "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing",
    "http://purl.oclc.org/ooxml/drawingml/picture":
        "http://schemas.openxmlformats.org/drawingml/2006/picture",
    "http://purl.oclc.org/ooxml/drawingml/chart":
        "http://schemas.openxmlformats.org/drawingml/2006/chart",
    "http://purl.oclc.org/ooxml/drawingml/main":
        "http://schemas.openxmlformats.org/drawingml/2006/main",
    "http://purl.oclc.org/ooxml/schemaLibrary/main":
        "http://schemas.openxmlformats.org/schemaLibrary/2006/main",
    "http://purl.oclc.org/ooxml/officeDocument/extendedProperties":
        "http://schemas.openxmlformats.org/officeDocument/2006/extended-properties",
    "http://purl.oclc.org/ooxml/officeDocument/docPropsVTypes":
        "http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes",
    "http://purl.oclc.org/ooxml/officeDocument/customXmlDataProps":
        "http://schemas.openxmlformats.org/officeDocument/2006/customXmlDataProps",
}

# Twips-valued attributes that strict writes with a unit suffix.
TWIPS_ATTRS = ("w:w", "w:h", "w:top", "w:right", "w:bottom", "w:left",
               "w:start", "w:end", "w:header", "w:footer", "w:gutter",
               "w:space", "w:firstLine", "w:hanging", "w:before", "w:after",
               "w:line", "w:tblpX", "w:tblpY", "w:hSpace", "w:vSpace",
               "w:leftFromText", "w:rightFromText", "w:val")

UNIT = {"pt": 20.0, "in": 1440.0, "cm": 1440 / 2.54, "mm": 144 / 2.54, "pc": 240.0}


def to_twips(match):
    attr, value, unit = match.group(1), match.group(2), match.group(3)
    return f'{attr}="{int(round(float(value) * UNIT[unit]))}"'


changed = 0
for path in root.rglob("*"):
    if path.suffix.lower() not in {".xml", ".rels"} or not path.is_file():
        continue
    text = original = path.read_text(encoding="utf-8")
    for strict, transitional in NS.items():
        text = text.replace(strict, transitional)
    pattern = r'\b(' + "|".join(TWIPS_ATTRS) + r')="(-?\d+(?:\.\d+)?)(' + "|".join(UNIT) + r')"'
    text = re.sub(pattern, to_twips, text)
    if text != original:
        path.write_text(text, encoding="utf-8")
        changed += 1
print(f"rewritten parts: {changed}")
