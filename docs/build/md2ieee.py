"""Render the conference-paper markdown into the IEEE template's document.xml.

Keeps the template's styles.xml/numbering.xml untouched, so heading numbering
(I., A.), table numbering (TABLE I.) and reference numbering ([1]) come from
the template itself -- the manual numbers in the markdown are stripped.
"""
import re, html, sys, pathlib

SRC = pathlib.Path(sys.argv[1])
UNPACKED = pathlib.Path(sys.argv[2])

# Transitional units (twips): US Letter, IEEE margins.
PGSZ = ('<w:pgSz w:w="12240" w:h="15840" w:code="1"/>'
        '<w:pgMar w:top="1080" w:right="907" w:bottom="1440" w:left="907"'
        ' w:header="720" w:footer="720" w:gutter="0"/>')
GRID = '<w:docGrid w:linePitch="360"/>'
SECT_1COL = (f'<w:sectPr><w:type w:val="continuous"/>{PGSZ}'
             f'<w:cols w:space="720"/>{GRID}</w:sectPr>')
SECT_2COL = (f'<w:sectPr><w:type w:val="continuous"/>{PGSZ}'
             f'<w:cols w:num="2" w:space="360"/>{GRID}</w:sectPr>')

def esc(t):
    return html.escape(t, quote=False).replace('"', '&quot;')

def runs(text):
    """Inline markdown -> w:r runs. Bold, italic, code, and [TO FILL] highlight."""
    out = []
    # protect TO FILL spans first
    tokens = re.split(r'(\*\*.+?\*\*|(?<!\*)\*(?!\*).+?(?<!\*)\*(?!\*)|`[^`]+`)', text, flags=re.S)
    for tok in tokens:
        if not tok:
            continue
        props, body = [], tok
        if tok.startswith('**') and tok.endswith('**'):
            props.append('<w:b/>'); body = tok[2:-2]
        elif tok.startswith('*') and tok.endswith('*'):
            props.append('<w:i/>'); body = tok[1:-1]
        elif tok.startswith('`') and tok.endswith('`'):
            body = tok[1:-1]
            props.append('<w:rFonts w:ascii="Consolas" w:hAnsi="Consolas"/>')
            props.append('<w:sz w:val="16"/>')
        if 'TO FILL' in body:
            props.append('<w:highlight w:val="yellow"/>'); props.append('<w:b/>')
        rpr = f'<w:rPr>{"".join(props)}</w:rPr>' if props else ''
        out.append(f'<w:r>{rpr}<w:t xml:space="preserve">{esc(body)}</w:t></w:r>')
    return ''.join(out) or '<w:r><w:t xml:space="preserve"></w:t></w:r>'

def para(style, text, sect=None):
    ppr = f'<w:pStyle w:val="{style}"/>' if style else ''
    if sect:
        ppr += sect
    ppr = f'<w:pPr>{ppr}</w:pPr>' if ppr else ''
    return f'<w:p>{ppr}{runs(text)}</w:p>'

def table(rows, full_width):
    ncol = len(rows[0])
    total = 10080 if full_width else 4680          # dxa
    w = total // ncol
    grid = ''.join(f'<w:gridCol w:w="{w}"/>' for _ in range(ncol))
    body = []
    for i, row in enumerate(rows):
        style = 'tablecolhead' if i == 0 else 'tablecopy'
        hdr = '<w:tblHeader/>' if i == 0 else ''
        cells = ''.join(
            f'<w:tc><w:tcPr><w:tcW w:w="{w}" w:type="dxa"/><w:vAlign w:val="center"/></w:tcPr>'
            f'<w:p><w:pPr><w:pStyle w:val="{style}"/></w:pPr>{runs(c)}</w:p></w:tc>'
            for c in row)
        body.append(f'<w:tr><w:trPr><w:cantSplit/>{hdr}<w:jc w:val="center"/></w:trPr>{cells}</w:tr>')
    return (
        '<w:tbl><w:tblPr><w:tblW w:w="0pt" w:type="dxa"/><w:jc w:val="center"/><w:tblBorders>'
        '<w:top w:val="single" w:sz="2" w:space="0" w:color="auto"/>'
        '<w:start w:val="single" w:sz="2" w:space="0" w:color="auto"/>'
        '<w:bottom w:val="single" w:sz="2" w:space="0" w:color="auto"/>'
        '<w:end w:val="single" w:sz="2" w:space="0" w:color="auto"/>'
        '<w:insideH w:val="single" w:sz="2" w:space="0" w:color="auto"/>'
        '<w:insideV w:val="single" w:sz="2" w:space="0" w:color="auto"/></w:tblBorders>'
        '<w:tblLayout w:type="fixed"/><w:tblLook w:firstRow="1" w:lastRow="0"'
        ' w:firstColumn="0" w:lastColumn="0" w:noHBand="0" w:noVBand="0"/></w:tblPr>'
        f'<w:tblGrid>{grid}</w:tblGrid>{"".join(body)}</w:tbl>')

# ---------------------------------------------------------------- parse
lines = SRC.read_text().split('\n')
# drop the editorial preamble: start at the Title marker
start = next(i for i, l in enumerate(lines) if l.startswith('**Title**'))
lines = lines[start:]

out = []
TITLE = 'Leveraging Foundational Models for Video Archival Data'
out.append(para('papertitle', TITLE))
out.append(para('Author', 'Saurav Vijay'))
out.append(para('Author',
                'School of Electronics, Electrical Engineering and Computer Science'))
out.append(para('Author', "Queen's University Belfast"))
out.append(f'<w:p><w:pPr>{SECT_1COL}</w:pPr></w:p>')

i = 0
in_refs = False
pending_tablehead = None
while i < len(lines):
    line = lines[i].rstrip()
    stripped = line.strip()

    if (not stripped or stripped in {'---'} or stripped.startswith('**Title**')
            or stripped.startswith('**Authors**')
            or stripped.startswith('Saurav Vijay ·')
            or stripped == TITLE
            or stripped.startswith('School of Electronics')):
        i += 1
        continue

    # blockquote -> highlighted note paragraph
    if stripped.startswith('>'):
        buf = []
        while i < len(lines) and lines[i].strip().startswith('>'):
            buf.append(lines[i].strip().lstrip('>').strip())
            i += 1
        text = ' '.join(x for x in buf if x).strip('`')
        if text:
            out.append(para('BodyText', text))
        continue

    # markdown table
    if stripped.startswith('|'):
        rows = []
        while i < len(lines) and lines[i].strip().startswith('|'):
            cells = [c.strip() for c in lines[i].strip().strip('|').split('|')]
            if not all(re.fullmatch(r':?-{2,}:?', c) for c in cells):
                rows.append(cells)
            i += 1
        full = len(rows[0]) >= 5
        if full:
            out.append(f'<w:p><w:pPr>{SECT_2COL}</w:pPr></w:p>')
            if pending_tablehead:
                out.append(pending_tablehead)
            out.append(table(rows, True))
            out.append(f'<w:p><w:pPr>{SECT_1COL}</w:pPr></w:p>')
        else:
            if pending_tablehead:
                out.append(pending_tablehead)
            out.append(table(rows, False))
        pending_tablehead = None
        continue

    # headings
    m = re.match(r'^(#{2,4})\s+(.*)$', stripped)
    if m:
        depth, text = len(m.group(1)), m.group(2)
        text = re.sub(r'\s*`\[[^\]]+\]`\s*$', '', text)          # drop style annotation
        text = re.sub(r'^(?:[IVX]+|[A-Z])\.\s+', '', text)        # style auto-numbers
        if text.lower().startswith('abstract'):
            i += 1
            continue
        if text.upper() == 'REFERENCES':
            in_refs = True
            out.append(para('Heading5', 'References'))
            i += 1
            continue
        if text.lower().startswith('contents'):
            i += 1
            continue
        style = {2: 'Heading1', 3: 'Heading2', 4: 'Heading3'}[depth]
        out.append(para(style, text if depth > 2 else text.title()
                        if text.isupper() else text))
        i += 1
        continue

    # abstract / keywords bodies
    if stripped.startswith('**Keywords**'):
        buf = [re.sub(r'^\*\*Keywords\*\*\s*`\[Keywords\]`\s*—?\s*', '', stripped)]
        i += 1
        while i < len(lines) and lines[i].strip() and not lines[i].strip().startswith(('#', '-', '|', '>')):
            buf.append(lines[i].strip()); i += 1
        out.append(para('Keywords', 'Keywords—' + ' '.join(buf)))
        continue

    # TABLE N. caption
    m = re.match(r'^TABLE\s+[IVX0-9]+\.\s*`\[tablehead\]`\s*(.*)$', stripped)
    if m:
        pending_tablehead = para('tablehead', m.group(1).title())
        i += 1
        continue

    # list items, joining any continuation lines
    m = re.match(r'^([-*]|\d+\.)\s+(.*)$', stripped)
    if m:
        marker, first = m.group(1), m.group(2)
        buf = [first]
        i += 1
        while (i < len(lines) and lines[i].strip()
               and not re.match(r'^(#{2,4}\s|\||>|---|[-*]\s|\d+\.\s|TABLE\s)',
                                lines[i].strip())
               and lines[i].startswith((' ', '\t'))):
            buf.append(lines[i].strip())
            i += 1
        text = ' '.join(buf)
        if marker in {'-', '*'}:
            out.append(para('bulletlist', text))
        else:
            out.append(para('BodyText', f'{marker} {text}'))
        continue

    # reference entries
    if in_refs:
        m = re.match(r'^\[\d+\]\s+(.*)$', stripped)
        if m:
            buf = [m.group(1)]
            i += 1
            while (i < len(lines) and lines[i].strip()
                   and not re.match(r'^(\[\d+\]|>|#)', lines[i].strip())):
                buf.append(lines[i].strip()); i += 1
            out.append(para('references', ' '.join(buf)))
            continue

    # ordinary paragraph (join wrapped lines)
    buf = [stripped]
    i += 1
    while (i < len(lines) and lines[i].strip()
           and not re.match(r'^(#{2,4}\s|\||>|---|\s*[-*]\s|\s*\d+\.\s|TABLE\s)', lines[i].strip())):
        buf.append(lines[i].strip()); i += 1
    text = ' '.join(buf)
    style = 'Abstract' if text.startswith('Community-television archives') else 'BodyText'
    out.append(para(style, text))

# ---------------------------------------------------------------- emit
doc = (UNPACKED / 'word/document.xml').read_text()
head = doc[:doc.index('<w:body>') + len('<w:body>')]
body = ''.join(out) + f'<w:sectPr>{PGSZ}<w:cols w:num="2" w:space="18pt"/></w:sectPr>'
(UNPACKED / 'word/document.xml').write_text(head + body + '</w:body></w:document>')
print(f'paragraphs/tables emitted: {len(out)}')
