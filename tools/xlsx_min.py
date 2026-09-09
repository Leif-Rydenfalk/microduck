"""Write a small .xlsx with the standard library only (inline strings, no styles beyond bold header).

    write_xlsx(path, {'Sheet name': [[header...], [row...], ...], ...})
"""
import zipfile
from xml.sax.saxutils import escape


def _col(n):
    s = ''
    while n:
        n, r = divmod(n-1, 26); s = chr(65+r)+s
    return s


def _sheet(rows):
    widths = {}
    out = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">']
    for r in rows:
        for j, v in enumerate(r):
            widths[j] = min(60, max(widths.get(j, 8), len(str(v if v is not None else ''))*1.1+2))
    if widths:
        out.append('<cols>'+''.join('<col min="%d" max="%d" width="%.1f" customWidth="1"/>' % (j+1, j+1, w) for j, w in sorted(widths.items()))+'</cols>')
    out.append('<sheetData>')
    for i, r in enumerate(rows, 1):
        cells = []
        for j, v in enumerate(r, 1):
            ref = _col(j)+str(i); style = ' s="1"' if i == 1 else ''
            if v is None or v == '': continue
            if isinstance(v, bool): cells.append('<c r="%s" t="b"%s><v>%d</v></c>' % (ref, style, v))
            elif isinstance(v, (int, float)): cells.append('<c r="%s"%s><v>%r</v></c>' % (ref, style, v))
            else: cells.append('<c r="%s" t="inlineStr"%s><is><t xml:space="preserve">%s</t></is></c>' % (ref, style, escape(str(v))))
        out.append('<row r="%d">%s</row>' % (i, ''.join(cells)))
    out.append('</sheetData><pageSetup orientation="landscape"/></worksheet>')
    return ''.join(out)


def write_xlsx(path, sheets):
    names = list(sheets)
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml', '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>'+''.join('<Override PartName="/xl/worksheets/sheet%d.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>' % (i+1) for i in range(len(names)))+'</Types>')
        z.writestr('_rels/.rels', '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>')
        z.writestr('xl/workbook.xml', '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets>'+''.join('<sheet name="%s" sheetId="%d" r:id="rId%d"/>' % (escape(n[:31]), i+1, i+1) for i, n in enumerate(names))+'</sheets></workbook>')
        z.writestr('xl/_rels/workbook.xml.rels', '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'+''.join('<Relationship Id="rId%d" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet%d.xml"/>' % (i+1, i+1) for i in range(len(names)))+'<Relationship Id="rId%d" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/></Relationships>' % (len(names)+1))
        z.writestr('xl/styles.xml', '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><fonts count="2"><font><sz val="11"/><name val="Calibri"/></font><font><b/><sz val="11"/><name val="Calibri"/></font></fonts><fills count="2"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill></fills><borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders><cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs><cellXfs count="2"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/><xf numFmtId="0" fontId="1" fillId="0" borderId="0" xfId="0" applyFont="1"/></cellXfs></styleSheet>')
        for i, n in enumerate(names):
            z.writestr('xl/worksheets/sheet%d.xml' % (i+1), _sheet(sheets[n]))
    return path
