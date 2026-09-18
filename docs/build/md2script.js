// Render the demo narration script as a teleprompter-style Word document:
// narration large enough to read aloud, stage directions visibly subordinate.
const fs = require('fs');
const {
  Document, Packer, Paragraph, TextRun, AlignmentType, BorderStyle,
  Table, TableRow, TableCell, WidthType, ShadingType,
} = require('docx');

const SRC = process.argv[2];
const OUT = process.argv[3];

const INK = '0B0B0B', MUTED = '52514E', RULE = 'D8D7D2', BAND = 'EFEFEC';

function inline(text, base = {}) {
  const runs = [];
  // \u23f8 in the source marks a beat where the reader stops and the screen works.
  text = text.replace(/\u23f8/g, '[PAUSE]');
  for (const part of text.split(/(\*\*.+?\*\*|(?<!\*)\*(?!\*)[^*]+\*(?!\*)|`[^`]+`|\[PAUSE\])/gs)) {
    if (!part) continue;
    let body = part, opts = { ...base };
    if (part === '[PAUSE]') { opts.bold = true; opts.color = MUTED; opts.size = (base.size || 24) - 4; }
    else if (part.startsWith('**') && part.endsWith('**')) { body = part.slice(2, -2); opts.bold = true; }
    else if (part.startsWith('*') && part.endsWith('*')) { body = part.slice(1, -1); opts.italics = true; }
    else if (part.startsWith('`') && part.endsWith('`')) {
      body = part.slice(1, -1); opts.font = 'Consolas'; opts.size = (base.size || 24) - 4;
    }
    runs.push(new TextRun({ text: body, ...opts }));
  }
  return runs.length ? runs : [new TextRun('')];
}

// A segment header sits in a shaded single-cell table so the timing is scannable
// when you are reading and recording at the same time.
function band(text) {
  return new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [9360],
    rows: [new TableRow({
      children: [new TableCell({
        shading: { type: ShadingType.CLEAR, fill: BAND, color: 'auto' },
        margins: { top: 90, bottom: 90, left: 140, right: 140 },
        borders: {
          top: { style: BorderStyle.NONE }, bottom: { style: BorderStyle.NONE },
          left: { style: BorderStyle.NONE }, right: { style: BorderStyle.NONE },
        },
        children: [new Paragraph({
          spacing: { after: 0 },
          children: [new TextRun({ text, bold: true, size: 26, color: INK })],
        })],
      })],
    })],
  });
}

const lines = fs.readFileSync(SRC, 'utf8').split('\n');
const out = [];
let i = 0, inChecklist = false;

while (i < lines.length) {
  const raw = lines[i], line = raw.trim();

  if (!line || line === '---') { i++; continue; }

  if (line.startsWith('# ')) {
    out.push(new Paragraph({
      alignment: AlignmentType.CENTER, spacing: { after: 120 },
      children: [new TextRun({ text: line.slice(2), bold: true, size: 36, color: INK })],
    }));
    i++; continue;
  }

  if (line.startsWith('## ')) {
    out.push(new Paragraph({ spacing: { before: 320, after: 120 }, children: [] }));
    out.push(band(line.slice(3).replace(/·/g, '·')));
    i++; continue;
  }

  // narration: consecutive '>' lines, set large for reading aloud
  if (line.startsWith('>')) {
    let buf = [];
    while (i < lines.length && lines[i].trim().startsWith('>')) {
      const t = lines[i].trim().replace(/^>\s?/, '');
      if (!t) { if (buf.length) { out.push(narration(buf.join(' '))); buf = []; } }
      else buf.push(t);
      i++;
    }
    if (buf.length) out.push(narration(buf.join(' ')));
    continue;
  }

  // checklist
  if (/^- \[ \]/.test(line)) {
    inChecklist = true;
    out.push(new Paragraph({
      spacing: { after: 100 }, indent: { left: 360, hanging: 260 },
      children: [new TextRun({ text: '☐  ', size: 24 }),
                 ...inline(line.replace(/^- \[ \]\s*/, ''), { size: 22, color: INK })],
    }));
    i++; continue;
  }

  // stage direction / ordinary note
  const isDirection = /^\*\*On screen:\*\*/.test(line);
  let buf = [line];
  i++;
  while (i < lines.length && lines[i].trim() && !/^(#|>|-|\*\*On screen)/.test(lines[i].trim())) {
    buf.push(lines[i].trim()); i++;
  }
  out.push(new Paragraph({
    spacing: { after: isDirection ? 160 : 140 },
    children: inline(buf.join(' '), {
      size: isDirection ? 20 : 21,
      italics: isDirection,
      color: isDirection ? MUTED : INK,
    }),
  }));
}

function narration(text) {
  return new Paragraph({
    spacing: { after: 200, line: 340, lineRule: 'auto' },
    indent: { left: 340 },
    border: { left: { style: BorderStyle.SINGLE, size: 12, color: RULE, space: 10 } },
    children: inline(text, { size: 26, color: INK }),   // 13pt, read-aloud size
  });
}

const doc = new Document({
  styles: { default: { document: { run: { font: 'Calibri', size: 22, color: INK } } } },
  sections: [{
    properties: { page: { margin: { top: 1080, right: 1440, bottom: 1080, left: 1440 } } },
    children: out,
  }],
});

Packer.toBuffer(doc).then((b) => { fs.writeFileSync(OUT, b); console.log('wrote', OUT); });
