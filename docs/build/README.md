# Regenerating the .docx files

The markdown in `docs/paper/` and `docs/report/` is the source of truth. Edit
there, then rebuild:

```bash
# Conference paper -> IEEE template
rm -rf /tmp/ieee && unzip -q docs/references/ieee-conference-template-letter.docx -d /tmp/ieee
find /tmp/ieee -type l -delete
python3 docs/build/strict2trans.py /tmp/ieee
python3 docs/build/md2ieee.py docs/paper/conference_paper.md /tmp/ieee
(cd /tmp/ieee && zip -Xrq - .) > docs/paper/conference_paper.docx

# Supporting materials -> single-column report
npm install docx        # once
node docs/build/md2report.js docs/report/supporting_materials.md \
                            docs/report/supporting_materials.docx
```

`md2ieee.py` writes the paper's body into the IEEE template's own
`document.xml`, leaving `styles.xml` and `numbering.xml` untouched — so the
section numbers (I., A.), table numbers (TABLE I.) and reference numbers ([1])
come from the template's numbering definitions, not from the markdown. The
manual numbers in the markdown are stripped during conversion; **do not
renumber by hand in Word**, or the numbers will double up.

`strict2trans.py` rewrites the template from ISO-Strict OOXML
(`purl.oclc.org/ooxml` namespaces, pt-suffixed measurements) to Transitional.
Word reads both; most other tooling, including LibreOffice, reads only
Transitional. The published template on disk is left untouched.

Wide tables (five or more columns) are emitted in their own single-column
section so they span both columns, which is the IEEE `table*` convention.
