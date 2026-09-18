// Render the supporting-materials markdown as a single-column US Letter report.
const fs = require('fs');
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType,
  Table, TableRow, TableCell, WidthType, ShadingType, BorderStyle,
  PageOrientation, TableOfContents, LevelFormat, PageBreak,
} = require('docx');

const SRC = process.argv[2];
const OUT = process.argv[3];

const CONTENT_W = 9360; // 12240 - 2*1440 twips

function inline(text, base = {}) {
  const runs = [];
  const parts = text.split(/(\*\*.+?\*\*|(?<!\*)\*(?!\*).+?(?<!\*)\*(?!\*)|`[^`]+`)/gs);
  for (const part of parts) {
    if (!part) continue;
    let body = part, opts = { ...base };
    if (part.startsWith('**') && part.endsWith('**')) { body = part.slice(2, -2); opts.bold = true; }
    else if (part.startsWith('*') && part.endsWith('*')) { body = part.slice(1, -1); opts.italics = true; }
    else if (part.startsWith('`') && part.endsWith('`')) {
      body = part.slice(1, -1); opts.font = 'Consolas'; opts.size = 18;
    }
    if (body.includes('TO FILL')) { opts.bold = true; opts.highlight = 'yellow'; }
    runs.push(new TextRun({ text: body, ...opts }));
  }
  return runs.length ? runs : [new TextRun('')];
}

function body(text, extra = {}) {
  return new Paragraph({
    children: inline(text),
    spacing: { after: 140, line: 276 },
    alignment: AlignmentType.JUSTIFIED,
    ...extra,
  });
}

function mdTable(rows) {
  const ncol = rows[0].length;
  const w = Math.floor(CONTENT_W / ncol);
  return new Table({
    columnWidths: Array(ncol).fill(w),
    width: { size: CONTENT_W, type: WidthType.DXA },
    rows: rows.map((cells, r) => new TableRow({
      tableHeader: r === 0,
      children: cells.map((c) => new TableCell({
        width: { size: w, type: WidthType.DXA },
        shading: r === 0
          ? { type: ShadingType.CLEAR, fill: 'EFEFEF', color: 'auto' }
          : undefined,
        margins: { top: 60, bottom: 60, left: 90, right: 90 },
        children: [new Paragraph({
          children: inline(c, r === 0 ? { bold: true } : {}),
          spacing: { after: 0 },
        })],
      })),
    })),
  });
}

const lines = fs.readFileSync(SRC, 'utf8').split('\n');
const children = [];
const front = [];

front.push(new Paragraph({
  children: [new TextRun({ text: 'Supporting Materials', bold: true, size: 44 })],
  alignment: AlignmentType.CENTER, spacing: { after: 160 },
}));
front.push(new Paragraph({
  children: [new TextRun({
    text: 'Leveraging Foundational Models for Video Archival Data',
    size: 28,
  })],
  alignment: AlignmentType.CENTER, spacing: { after: 100 },
}));
front.push(new Paragraph({
  children: [new TextRun({
    text: "NVTV public archive · Saurav Vijay · MSc Artificial Intelligence · Queen's University Belfast",
    size: 20, color: '555555',
  })],
  alignment: AlignmentType.CENTER, spacing: { after: 320 },
}));

let i = 0;
let started = false;
while (i < lines.length) {
  const raw = lines[i];
  const line = raw.trim();

  if (!line || line === '---') { i++; continue; }

  // skip the editorial preamble and the markdown contents list (a field TOC replaces it)
  if (!started) {
    if (/^##\s+1\.\s/.test(line)) { started = true; } else { i++; continue; }
  }

  if (line.startsWith('>')) {
    const buf = [];
    while (i < lines.length && lines[i].trim().startsWith('>')) {
      buf.push(lines[i].trim().replace(/^>\s?/, '')); i++;
    }
    const text = buf.filter(Boolean).join(' ').replace(/^`|`$/g, '');
    if (text) {
      children.push(new Paragraph({
        children: inline(text),
        spacing: { after: 160, before: 80, line: 276 },
        indent: { left: 360 },
        border: { left: { style: BorderStyle.SINGLE, size: 12, color: 'C0C0C0', space: 8 } },
      }));
    }
    continue;
  }

  if (line.startsWith('|')) {
    const rows = [];
    while (i < lines.length && lines[i].trim().startsWith('|')) {
      const cells = lines[i].trim().replace(/^\||\|$/g, '').split('|').map((c) => c.trim());
      if (!cells.every((c) => /^:?-{2,}:?$/.test(c))) rows.push(cells);
      i++;
    }
    children.push(mdTable(rows));
    children.push(new Paragraph({ text: '', spacing: { after: 160 } }));
    continue;
  }

  const h = line.match(/^(#{2,4})\s+(.*)$/);
  if (h) {
    const depth = h[1].length;
    const level = { 2: HeadingLevel.HEADING_1, 3: HeadingLevel.HEADING_2, 4: HeadingLevel.HEADING_3 }[depth];
    children.push(new Paragraph({
      children: inline(h[2], { bold: true, size: depth === 2 ? 28 : depth === 3 ? 24 : 22 }),
      heading: level,
      spacing: { before: depth === 2 ? 400 : 260, after: 140 },
      pageBreakBefore: depth === 2 && children.length > 0,
    }));
    i++;
    continue;
  }

  const li = line.match(/^([-*]|\d+\.)\s+(.*)$/);
  if (li) {
    const buf = [li[2]];
    i++;
    while (i < lines.length && lines[i].trim()
           && /^[ \t]/.test(lines[i])
           && !/^(#{2,4}\s|\||>|---|[-*]\s|\d+\.\s)/.test(lines[i].trim())) {
      buf.push(lines[i].trim()); i++;
    }
    const text = buf.join(' ');
    if (/^[-*]$/.test(li[1])) {
      children.push(new Paragraph({
        children: inline(text), bullet: { level: 0 },
        spacing: { after: 90, line: 276 },
      }));
    } else {
      children.push(new Paragraph({
        children: inline(`${li[1]} ${text}`),
        indent: { left: 360, hanging: 360 },
        spacing: { after: 90, line: 276 },
      }));
    }
    continue;
  }

  if (line.startsWith('```')) {
    i++;
    const buf = [];
    while (i < lines.length && !lines[i].trim().startsWith('```')) { buf.push(lines[i]); i++; }
    i++;
    for (const l of buf) {
      children.push(new Paragraph({
        children: [new TextRun({ text: l || ' ', font: 'Consolas', size: 18 })],
        spacing: { after: 0 }, indent: { left: 360 },
        shading: { type: ShadingType.CLEAR, fill: 'F4F4F4', color: 'auto' },
      }));
    }
    children.push(new Paragraph({ text: '', spacing: { after: 140 } }));
    continue;
  }

  const buf = [line];
  i++;
  while (i < lines.length && lines[i].trim()
         && !/^(#{2,4}\s|\||>|---|[-*]\s|\d+\.\s|```)/.test(lines[i].trim())) {
    buf.push(lines[i].trim()); i++;
  }
  children.push(body(buf.join(' ')));
}

const doc = new Document({
  styles: {
    default: {
      document: { run: { font: 'Times New Roman', size: 22 } },
      heading1: { run: { font: 'Times New Roman', color: '000000' } },
      heading2: { run: { font: 'Times New Roman', color: '000000' } },
      heading3: { run: { font: 'Times New Roman', color: '000000' } },
    },
  },
  sections: [{
    properties: {
      page: {
        size: { width: 12240, height: 15840, orientation: PageOrientation.PORTRAIT },
        margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 },
      },
    },
    children: [
      ...front,
      new Paragraph({
        children: [new TextRun({ text: 'Contents', bold: true, size: 28 })],
        spacing: { before: 200, after: 160 },
      }),
      new TableOfContents('Contents', { hyperlink: true, headingStyleRange: '1-3' }),
      new Paragraph({
        children: [new TextRun({
          text: 'Right-click the contents field in Word and choose "Update Field" to populate it.',
          size: 18, italics: true, color: '777777',
        })],
        spacing: { after: 120 },
      }),
      ...children,
    ],
  }],
});

Packer.toBuffer(doc).then((b) => { fs.writeFileSync(OUT, b); console.log('wrote', OUT); });
