#!/usr/bin/env python3
"""Eksport tanaman.db ke tanaman.xlsx (satu helaian bagi setiap jadual)."""
import sqlite3
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

HERE = Path(__file__).resolve().parent
con = sqlite3.connect(HERE / "tanaman.db")

FONT = "Arial"
HDR_FILL = PatternFill("solid", start_color="2E5E3E")
HDR_FONT = Font(name=FONT, bold=True, color="FFFFFF")
BODY_FONT = Font(name=FONT)
NOTE_FONT = Font(name=FONT, italic=True, color="666666", size=9)
INPUT_FILL = PatternFill("solid", start_color="FFFF00")
THIN = Side(style="thin", color="BFBFBF")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
SUMBER = "Sumber data: maklumat tanaman yang diberikan oleh pengguna (rujukan TNAU dan Nepal seperti dinyatakan)."

# (nama helaian, query, lebar lajur)
SHEETS = [
    ("Perbandingan", """
        SELECT tanaman AS Tanaman, jenis AS Jenis, julat_ph AS "pH", suhu_c AS "Suhu (°C)",
               air_mm AS "Air (mm)", nitrogen AS Nitrogen, nutrien_utama AS "Nutrien utama",
               peringkat_kritikal_air AS "Peringkat kritikal air", matang_hari AS "Matang (hari)"
        FROM v_perbandingan""",
     [14, 10, 10, 11, 12, 34, 26, 34, 13]),
    ("Tanaman", """
        SELECT nama_bm AS Tanaman, nama_en AS "Nama Inggeris", nama_saintifik AS "Nama saintifik",
               jenis AS Jenis, CASE menetapkan_n WHEN 1 THEN 'Ya' ELSE 'Tidak' END AS "Menetapkan N",
               nutrien_utama AS "Nutrien utama", keperluan_n AS "Keperluan N",
               suhu_min_c AS "Suhu min (°C)", suhu_max_c AS "Suhu maks (°C)",
               air_min_mm AS "Air min (mm)", air_max_mm AS "Air maks (mm)",
               air_sasaran_mm AS "Air sasaran (mm)", air_nota AS "Nota air",
               matang_min_hari AS "Matang min (hari)", matang_max_hari AS "Matang maks (hari)",
               matang_nota AS "Nota matang", sumber_rujukan AS "Sumber rujukan"
        FROM tanaman ORDER BY id""",
     [14, 13, 18, 10, 13, 26, 34, 13, 14, 12, 13, 15, 40, 16, 17, 30, 26]),
    ("Tanah", """
        SELECT t.nama_bm AS Tanaman, k.tekstur AS Tekstur, k.saliran AS Saliran,
               k.ph_min AS "pH min", k.ph_max AS "pH maks", k.ph_elak_bawah AS "Elak pH bawah",
               k.nota AS Nota
        FROM keperluan_tanah k JOIN tanaman t ON t.id = k.tanaman_id ORDER BY t.id""",
     [14, 28, 10, 9, 9, 14, 44]),
    ("Air Kritikal", """
        SELECT t.nama_bm AS Tanaman, p.peringkat AS "Peringkat kritikal"
        FROM peringkat_kritikal_air p JOIN tanaman t ON t.id = p.tanaman_id ORDER BY t.id, p.id""",
     [14, 28]),
    ("Baja NPK", """
        SELECT t.nama_bm AS Tanaman, b.sumber AS Sumber, b.keadaan AS Keadaan,
               b.n_min AS "N min", b.n_max AS "N maks",
               b.p2o5_min AS "P₂O₅ min", b.p2o5_max AS "P₂O₅ maks",
               b.k2o_min AS "K₂O min", b.k2o_max AS "K₂O maks", b.nota AS Nota
        FROM cadangan_baja b JOIN tanaman t ON t.id = b.tanaman_id ORDER BY t.id, b.id""",
     [14, 10, 18, 8, 8, 10, 10, 9, 9, 32]),
    ("Program Baja", """
        SELECT t.nama_bm AS Tanaman, p.jenis_baja AS "Jenis baja", p.kadar_min AS "Kadar min",
               p.kadar_max AS "Kadar maks", p.unit AS Unit, p.masa_aplikasi AS "Masa aplikasi",
               p.nota AS Nota
        FROM program_baja p JOIN tanaman t ON t.id = p.tanaman_id ORDER BY t.id, p.id""",
     [14, 34, 10, 11, 13, 34, 46]),
    ("Nutrien Khusus", """
        SELECT t.nama_bm AS Tanaman, n.nutrien AS Nutrien, n.kepentingan AS Kepentingan,
               n.sumber_baja AS "Sumber baja", n.kadar_min_kg_ha AS "Kadar min (kg/ha)",
               n.kadar_max_kg_ha AS "Kadar maks (kg/ha)", n.masa_aplikasi AS "Masa aplikasi"
        FROM nutrien_khusus n JOIN tanaman t ON t.id = n.tanaman_id ORDER BY t.id, n.id""",
     [14, 17, 32, 13, 16, 17, 38]),
    ("Amalan", """
        SELECT t.nama_bm AS Tanaman, a.kategori AS Kategori, a.perkara AS Perkara
        FROM amalan a JOIN tanaman t ON t.id = a.tanaman_id ORDER BY t.id, a.id""",
     [14, 10, 62]),
    ("Jarak Tanaman", """
        SELECT t.nama_bm AS Tanaman, j.jenis_varieti AS "Jenis varieti",
               j.antara_baris_min_cm AS "Antara baris min (cm)", j.antara_baris_max_cm AS "Antara baris maks (cm)",
               j.dalam_baris_min_cm AS "Dalam baris min (cm)", j.dalam_baris_max_cm AS "Dalam baris maks (cm)"
        FROM jarak_tanaman j JOIN tanaman t ON t.id = j.tanaman_id ORDER BY t.id, j.id""",
     [14, 14, 20, 21, 19, 20]),
    ("Giliran Tanaman", """
        SELECT s.nama_bm AS "Tanaman sebelum", e.nama_bm AS "Tanaman selepas",
               g.kesan_hasil_peratus AS "Kesan hasil (%)", g.nota AS Nota
        FROM giliran_tanaman g
        JOIN tanaman s ON s.id = g.tanaman_sebelum_id
        JOIN tanaman e ON e.id = g.tanaman_selepas_id ORDER BY g.id""",
     [17, 16, 15, 60]),
]

UNIT_NOTE = "Unit: suhu °C, air mm/musim, baja kg/ha, jarak cm, tempoh dalam hari. Sel kosong = tiada data."


def style_header(ws, ncols, row=1):
    for c in range(1, ncols + 1):
        cell = ws.cell(row=row, column=c)
        cell.font, cell.fill, cell.border = HDR_FONT, HDR_FILL, BORDER
        cell.alignment = Alignment(wrap_text=True, vertical="center")


wb = Workbook()
wb.remove(wb.active)

for name, sql, widths in SHEETS:
    ws = wb.create_sheet(name)
    cur = con.execute(sql)
    headers = [d[0] for d in cur.description]
    ws.append(headers)
    rows = cur.fetchall()
    for r in rows:
        ws.append(list(r))
    style_header(ws, len(headers))
    for row in ws.iter_rows(min_row=2, max_row=len(rows) + 1, max_col=len(headers)):
        for cell in row:
            cell.font, cell.border = BODY_FONT, BORDER
            cell.alignment = Alignment(wrap_text=True, vertical="top")
            if isinstance(cell.value, float):
                cell.number_format = "0.0" if ("pH" in str(ws.cell(1, cell.column).value) or cell.value % 1) else "0"
    for i, w in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.freeze_panes = "B2"
    ws.auto_filter.ref = f"A1:{get_column_letter(len(headers))}{len(rows) + 1}"
    n = len(rows) + 3
    ws.cell(n, 1, UNIT_NOTE).font = NOTE_FONT
    ws.cell(n + 1, 1, SUMBER).font = NOTE_FONT

# Nota giliran umum di bawah helaian Giliran Tanaman
ws = wb["Giliran Tanaman"]
start = ws.max_row + 2
ws.cell(start, 1, "Nota umum giliran tanaman").font = Font(name=FONT, bold=True)
for i, (nota,) in enumerate(con.execute("SELECT nota FROM nota_giliran ORDER BY id"), start=1):
    ws.cell(start + i, 1, f"• {nota}").font = BODY_FONT

# ---------------------------------------------------------------------
# Helaian Semak Kesesuaian: masukkan pH/suhu tanah, formula semak setiap tanaman
# ---------------------------------------------------------------------
ws = wb.create_sheet("Semak Kesesuaian", 0)
ws["A1"] = "Semak kesesuaian tanaman"
ws["A1"].font = Font(name=FONT, bold=True, size=14)
ws["A2"] = "Isi sel kuning sahaja. Keputusan dikira secara automatik daripada helaian Tanah dan Tanaman."
ws["A2"].font = NOTE_FONT

inputs = [("pH tanah", 5.8, "0.0"), ("Suhu purata (°C)", 28, "0"), ("Air tersedia semusim (mm)", 600, "0")]
for i, (label, val, fmt) in enumerate(inputs, start=4):
    ws.cell(i, 1, label).font = Font(name=FONT, bold=True)
    c = ws.cell(i, 2, val)
    c.font = Font(name=FONT, color="0000FF")
    c.fill, c.border, c.number_format = INPUT_FILL, BORDER, fmt
ws["C4"] = "Contoh nilai — tukar kepada data ladang awak."
ws["C4"].font = NOTE_FONT
dv = DataValidation(type="decimal", operator="between", formula1="0", formula2="14",
                    error="pH mesti antara 0 dan 14", showErrorMessage=True)
ws.add_data_validation(dv)
dv.add("B4")

hdr = ["Tanaman", "pH", "Suhu", "Air", "Keputusan"]
for c, h in enumerate(hdr, start=1):
    ws.cell(8, c, h)
style_header(ws, len(hdr), row=8)

n_crops = con.execute("SELECT COUNT(*) FROM tanaman").fetchone()[0]
for i in range(n_crops):
    r = 9 + i
    src = i + 2  # baris sepadan dalam helaian Tanah / Tanaman (susunan id sama)
    ws.cell(r, 1, f"=Tanaman!A{src}")
    ws.cell(r, 2, f'=IF(AND($B$4>=Tanah!D{src},$B$4<=Tanah!E{src}),"Sesuai","Tidak sesuai")')
    ws.cell(r, 3, f'=IF(AND($B$5>=Tanaman!H{src},$B$5<=Tanaman!I{src}),"Optimum","Luar julat optimum")')
    ws.cell(r, 4, f'=IF(Tanaman!J{src}="","Tiada angka mm — kekalkan tanah lembap",'
                  f'IF($B$6<Tanaman!J{src},"Kurang — perlu pengairan",'
                  f'IF($B$6>Tanaman!K{src},"Berlebihan — pastikan saliran","Mencukupi")))')
    ws.cell(r, 5, f'=IF(AND(B{r}="Sesuai",C{r}="Optimum",OR(D{r}="Mencukupi",LEFT(D{r},5)="Tiada")),"✔ Sesuai ditanam","⚠ Perlu perhatian")')
    for c in range(1, 6):
        cell = ws.cell(r, c)
        cell.font, cell.border = BODY_FONT, BORDER
        cell.alignment = Alignment(wrap_text=True, vertical="top")

for col, w in zip("ABCDE", [28, 14, 20, 30, 22]):
    ws.column_dimensions[col].width = w
note_row = 9 + n_crops + 1
ws.cell(note_row, 1, "Julat yang digunakan: pH (helaian Tanah), suhu optimum dan air semusim (helaian Tanaman).").font = NOTE_FONT
ws.cell(note_row + 1, 1, SUMBER).font = NOTE_FONT

out = HERE / "tanaman.xlsx"
wb.save(out)
print(f"Siap: {out}")
