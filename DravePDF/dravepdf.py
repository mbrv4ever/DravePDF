#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DravePDF - PDF-gereedschap + ondertekenen (DraveSign).
Tabblad 1: samenvoegen, splitsen, pagina's draaien/verwijderen.
Tabblad 2: onderteken met je getypte naam in een nette letter.
Dravenlock-huisstijl, offline, toegankelijk, OS-taal. Donationware.
"""
import os
import sys
import json

try:
    import pymupdf as fitz
except Exception:
    try:
        import fitz
    except Exception:
        fitz = None

from PyQt6.QtCore import Qt, QUrl, QLocale, QSize, QRect, pyqtSignal, QMarginsF
from PyQt6.QtGui import (QPixmap, QImage, QIcon, QDesktopServices, QColor, QFont,
                         QTextCharFormat, QTextImageFormat, QTextDocument,
                         QPdfWriter, QPageSize, QPageLayout, QTextCursor)
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton, QToolButton,
    QVBoxLayout, QHBoxLayout, QScrollArea, QFileDialog, QComboBox, QLineEdit,
    QMessageBox, QDialog, QSpinBox, QFrame, QPlainTextEdit, QStatusBar,
    QTabWidget, QListWidget, QListWidgetItem, QAbstractItemView, QStackedWidget,
    QTextEdit, QInputDialog)

APP_NAME = "DravePDF"
APP_VERSION = "0.17.3"
DONATE_URL = "https://paypal.me/roger076"
SUPPORT_MAIL = "service@dravenlock.nl"

BG = "#0e0e11"
PANEL = "#16161b"
TILE = "#1a1a20"
SILVER = "#d4d4d4"
MUTE = "#8a8a94"
ACCENT = "#6fa3d6"
WARN = "#e0a23a"


# ---------------------------------------------------------------------------
# Paden
# ---------------------------------------------------------------------------
def _app_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def _resource(name):
    for base in (getattr(sys, "_MEIPASS", None), _app_dir()):
        if base:
            p = os.path.join(base, name)
            if os.path.exists(p):
                return p
    return os.path.join(_app_dir(), name)


def _config_path():
    return os.path.join(_app_dir(), "dravepdf_config.json")


DEFAULT_CONFIG = {"lang": "", "last_dir": ""}


def load_config():
    cfg = dict(DEFAULT_CONFIG)
    try:
        with open(_config_path(), "r", encoding="utf-8") as f:
            cfg.update(json.load(f))
    except Exception:
        pass
    return cfg


def save_config(cfg):
    try:
        with open(_config_path(), "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Taal
# ---------------------------------------------------------------------------
_LANG = "nl"

TRANSLATIONS = {
    "en": {
        "PDF-gereedschap": "PDF tools", "Ondertekenen": "Sign",
        "Openen\u2026": "Open\u2026", "Opslaan als\u2026": "Save as\u2026",
        "Samenvoegen\u2026": "Merge\u2026", "Splitsen\u2026": "Split\u2026",
        "Draai links": "Rotate left", "Draai rechts": "Rotate right",
        "Pagina's verwijderen": "Delete pages",
        "Alles selecteren": "Select all", "Niets selecteren": "Select none",
        "Instellingen\u2026": "Settings\u2026", "Snelgids": "Quick guide",
        "Over": "About", "Sluiten": "Close", "Taal:": "Language:",
        "Automatisch (OS)": "Automatic (OS)", "Nederlands": "Dutch",
        "Engels": "English", "Donatie": "Donate",
        "PDF-bestanden (*.pdf)": "PDF files (*.pdf)",
        "Alle bestanden (*)": "All files (*)",
        "Open een PDF om te beginnen": "Open a PDF to get started",
        "Pagina": "Page", "van": "of", "Vorige": "Previous", "Volgende": "Next",
        "Kon niet openen": "Could not open", "Kon niet opslaan": "Could not save",
        "Opgeslagen": "Saved", "Opgeslagen als": "Saved as",
        "pagina": "page", "pagina's": "pages", "geselecteerd": "selected",
        "Geen pagina's geselecteerd.": "No pages selected.",
        "Kies de map voor de losse pagina's": "Choose the folder for the single pages",
        "Klaar: %d bestanden weggeschreven.": "Done: %d files written.",
        "PDF's samenvoegen (kies 2 of meer)": "Merge PDFs (pick 2 or more)",
        "Naam:": "Name:", "Lettertype:": "Font:", "Grootte:": "Size:",
        "Kleur:": "Colour:", "Zwart": "Black", "Blauw": "Blue",
        "Sierlijk (Times cursief)": "Elegant (Times italic)",
        "Sierlijk vet (Times)": "Elegant bold (Times)",
        "Zakelijk (Helvetica)": "Business (Helvetica)",
        "Typemachine (Courier)": "Typewriter (Courier)",
        "Klik op de pagina om je handtekening te plaatsen.":
            "Click on the page to place your signature.",
        "Onderteken en opslaan als\u2026": "Sign and save as\u2026",
        "Typ eerst je naam.": "Type your name first.",
        "Plaats eerst je handtekening (klik op de pagina).":
            "Place your signature first (click on the page).",
        "Ondertekend en opgeslagen.": "Signed and saved.",
        "Inzoomen": "Zoom in", "Uitzoomen": "Zoom out", "Passend": "Fit width",
        "snelgids_titel": "DravePDF - quick guide",
        "Maken": "Create", "Titel:": "Title:", "Paginaformaat:": "Page size:",
        "PDF maken\u2026": "Create PDF\u2026",
        "Afbeeldingen naar PDF\u2026": "Images to PDF\u2026",
        "Typ hier je tekst\u2026": "Type your text here\u2026",
        "Geen tekst om op te slaan.": "No text to save.",
        "PDF gemaakt.": "PDF created.",
        "Afbeeldingen (*.png *.jpg *.jpeg *.bmp *.gif)":
            "Images (*.png *.jpg *.jpeg *.bmp *.gif)",
        "Klassiek (Times)": "Classic (Times)", "Times cursief": "Times italic",
        "Afbeelding invoegen\u2026": "Insert image\u2026",
        "Link invoegen\u2026": "Insert link\u2026",
        "Rood": "Red", "Groen": "Green",
        "Sjabloon\u2026": "Template\u2026", "Leeg": "Blank",
        "Standaard document": "Standard document", "Zakelijke brief": "Business letter",
        "Memo / notitie": "Memo / note", "Uitnodiging": "Invitation",
        "De huidige tekst vervangen door het sjabloon?":
            "Replace the current text with the template?",
        "Bewerken": "Edit", "Tekst plaatsen": "Place text",
        "Afbeelding plaatsen": "Place image", "Kies afbeelding\u2026": "Choose image\u2026",
        "Breedte:": "Width:", "Tekst:": "Text:",
        "Ongedaan maken": "Undo", "Opnieuw beginnen": "Start over",
        "Klik op de pagina om te plaatsen.": "Click on the page to place.",
        "Klik om te plaatsen; sleep om te verplaatsen; rechtsklik verwijdert.":
            "Click to place; drag to move; right-click to remove.",
        "Er is nog niets geplaatst.": "Nothing has been placed yet.",
        "Verwijderen": "Delete", "Wissen": "Erase", "Tekst\u2026": "Text\u2026",
        "Selecteren": "Select",
        "Klik op de pagina en typ:": "Click on the page and type:",
        "Link:": "Link:", "Link\u2026": "Link\u2026", "Link \u2713": "Link \u2713",
        "Selecteer eerst een tekstvak.": "Select a text box first.",
        "Link toegevoegd.": "Link added.", "Link verwijderd.": "Link removed.",
        "Link toegevoegd. Sleep hem naar de juiste plek.":
            "Link added. Drag it to the right spot.",
        "URL (https://...) voor het geselecteerde stuk tekst:":
            "URL (https://...) for the selected piece of text:",
        "Klik een item om het te selecteren, sleep om te verplaatsen, dubbelklik tekst om te wijzigen.":
            "Click an item to select it, drag to move, double-click text to edit.",
        "Sleep een vak over wat je wilt weghalen.":
            "Drag a box over what you want to remove.",
        "Klik om te plaatsen; sleep om te verplaatsen; klik een item om het aan te passen; rechtsklik verwijdert.":
            "Click to place; drag to move; click an item to edit it; right-click to remove.",
        "Kies eerst een afbeelding.": "Choose an image first.",
        "Typ eerst tekst.": "Type text first.",
        "Niet-opgeslagen wijzigingen": "Unsaved changes",
        "Er zijn wijzigingen. Toch sluiten?": "There are changes. Close anyway?",
        "bestanden": "files",
    }
}


def detect_lang(cfg):
    forced = (cfg.get("lang") or "").strip().lower()
    if forced in ("nl", "en"):
        return forced
    try:
        if QLocale.system().name().lower().startswith("nl"):
            return "nl"
        return "en"
    except Exception:
        return "nl"


def t(s, lang=None):
    lg = lang or _LANG
    if lg == "nl":
        return s
    return TRANSLATIONS.get(lg, {}).get(s, s)


def safe_filename(name, fallback="document"):
    """Maakt van een titel een veilige bestandsnaam (zonder verboden tekens)."""
    name = (name or "").strip()
    for ch in '<>:"/\\|?*\n\r\t':
        name = name.replace(ch, " ")
    name = " ".join(name.split())
    return name[:120] or fallback


# ---------------------------------------------------------------------------
# Logo
# ---------------------------------------------------------------------------
def logo_pixmap(size=64):
    p = _resource("logo.png")
    if os.path.exists(p):
        pm = QPixmap(p)
        if not pm.isNull():
            return pm.scaled(size, size, Qt.AspectRatioMode.KeepAspectRatio,
                             Qt.TransformationMode.SmoothTransformation)
    pm = QPixmap(size, size)
    pm.fill(Qt.GlobalColor.transparent)
    return pm


def app_icon():
    return QIcon(logo_pixmap(64))


# ---------------------------------------------------------------------------
# PDF-bewerkingen (los testbaar)
# ---------------------------------------------------------------------------
def merge_pdfs(paths, out_path):
    if fitz is None:
        return False, "PyMuPDF ontbreekt (pymupdf)."
    try:
        new = fitz.open()
        for p in paths:
            src = fitz.open(p)
            new.insert_pdf(src)
            src.close()
        new.save(out_path, garbage=4, deflate=True)
        new.close()
        return True, out_path
    except Exception as e:
        return False, str(e)


def split_pdf(path, out_dir, pages=None):
    """Schrijft elke (geselecteerde) pagina als los PDF. Geeft (ok, aantal/melding)."""
    if fitz is None:
        return False, "PyMuPDF ontbreekt (pymupdf)."
    try:
        doc = fitz.open(path)
        base = os.path.splitext(os.path.basename(path))[0]
        nums = pages if pages else list(range(doc.page_count))
        count = 0
        for i in nums:
            single = fitz.open()
            single.insert_pdf(doc, from_page=i, to_page=i)
            single.save(os.path.join(out_dir, "%s_p%d.pdf" % (base, i + 1)),
                        garbage=4, deflate=True)
            single.close()
            count += 1
        doc.close()
        return True, count
    except Exception as e:
        return False, str(e)


def rotate_pages(doc, pnos, delta):
    for i in pnos:
        page = doc[i]
        page.set_rotation((page.rotation + delta) % 360)
    return True


def delete_pages(doc, pnos):
    keep = [i for i in range(doc.page_count) if i not in set(pnos)]
    if not keep:
        return False
    doc.select(keep)
    return True


def sign_text(doc, pno, point_pdf, text, fontname, fontsize, color):
    page = doc[pno]
    page.insert_text(point_pdf, text, fontname=fontname, fontsize=fontsize,
                     color=color)
    return True


def save_doc(doc, out_path, src_path=None):
    """Slaat altijd eerst op naar een tijdelijk bestand en zet dat daarna op
    z'n plek. Zo schrijven we NOOIT rechtstreeks over het geopende bestand
    (PyMuPDF staat dat niet toe -> 'save to original must be incremental').
    Geeft een (mogelijk heropend) doc terug."""
    tmp = out_path + ".dpdfsave.tmp"
    doc.save(tmp, garbage=4, deflate=True)
    # is out_path het bestand dat dit doc geopend heeft? dan dichtdoen en heropenen
    reopen = False
    try:
        if doc.name and os.path.exists(out_path) and os.path.samefile(doc.name, out_path):
            reopen = True
    except Exception:
        if src_path and (os.path.normcase(os.path.abspath(out_path))
                         == os.path.normcase(os.path.abspath(src_path))):
            reopen = True
    if reopen:
        doc.close()
    os.replace(tmp, out_path)
    if reopen:
        return fitz.open(out_path)
    return doc


# ---------------------------------------------------------------------------
# PDF maken (van tekst of afbeeldingen)
# ---------------------------------------------------------------------------
PAGE_SIZES = [("A4", (595, 842)), ("Letter", (612, 792))]


def text_to_pdf(out_path, title, body, pagesize, fontcode, fontsize, color):
    """Maakt een PDF van getypte tekst, met automatische pagina-afbreking."""
    if fitz is None:
        return False, "PyMuPDF ontbreekt (pymupdf)."
    try:
        W, H = pagesize
        margin = 56
        maxw = W - 2 * margin
        doc = fitz.open()
        page = doc.new_page(width=W, height=H)
        y = margin
        if title.strip():
            tsize = max(fontsize + 8, 18)
            page.insert_text((margin, y + tsize), title, fontname=fontcode,
                             fontsize=tsize, color=color)
            y += tsize * 1.8
        lh = fontsize * 1.45

        def wrap(par):
            words = par.split(" ")
            lines, cur = [], ""
            for wd in words:
                test = (cur + " " + wd).strip()
                if not cur or fitz.get_text_length(
                        test, fontname=fontcode, fontsize=fontsize) <= maxw:
                    cur = test
                else:
                    lines.append(cur)
                    cur = wd
            if cur:
                lines.append(cur)
            return lines or [""]

        for par in body.split("\n"):
            for line in wrap(par):
                if y + lh > H - margin:
                    page = doc.new_page(width=W, height=H)
                    y = margin
                page.insert_text((margin, y + fontsize), line,
                                 fontname=fontcode, fontsize=fontsize, color=color)
                y += lh
            y += lh * 0.3
        doc.save(out_path, garbage=4, deflate=True)
        doc.close()
        return True, out_path
    except Exception as e:
        return False, str(e)


def images_to_pdf(out_path, paths):
    """Maakt een PDF met elke afbeelding als eigen pagina."""
    if fitz is None:
        return False, "PyMuPDF ontbreekt (pymupdf)."
    try:
        doc = fitz.open()
        used = 0
        for img in paths:
            try:
                pix = fitz.Pixmap(img)
            except Exception:
                continue
            page = doc.new_page(width=pix.width, height=pix.height)
            page.insert_image(page.rect, filename=img)
            used += 1
        if used == 0:
            doc.close()
            return False, "geen geldige afbeeldingen"
        doc.save(out_path, garbage=4, deflate=True)
        doc.close()
        return True, out_path
    except Exception as e:
        return False, str(e)


# ---------------------------------------------------------------------------
# Pagina-render-helper
# ---------------------------------------------------------------------------
def render_page(doc, pno, zoom):
    page = doc[pno]
    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=False)
    img = QImage(pix.samples, pix.width, pix.height, pix.stride,
                 QImage.Format.Format_RGB888)
    return img.copy(), pix.width, pix.height


def thumb(doc, pno, w=120):
    page = doc[pno]
    r = page.rect
    z = w / (r.width or 120)
    pix = page.get_pixmap(matrix=fitz.Matrix(z, z), alpha=False)
    img = QImage(pix.samples, pix.width, pix.height, pix.stride,
                 QImage.Format.Format_RGB888).copy()
    return QPixmap.fromImage(img)


# ===========================================================================
# Tabblad 1: PDF-gereedschap
# ===========================================================================
class ToolsTab(QWidget):
    status = pyqtSignal(str)

    def __init__(self, get_lang, get_dir, set_dir):
        super().__init__()
        self.get_lang = get_lang
        self.get_dir = get_dir
        self.set_dir = set_dir
        self.doc = None
        self.path = None
        self.dirty = False

        lay = QVBoxLayout(self)
        lay.setContentsMargins(12, 12, 12, 12)
        lay.setSpacing(8)

        bar = QHBoxLayout()
        bar.setSpacing(8)
        self.b_open = QPushButton(t("Openen\u2026", self.get_lang()))
        self.b_open.setObjectName("primary")
        self.b_open.clicked.connect(self.open_pdf)
        bar.addWidget(self.b_open)
        self.b_merge = QPushButton(t("Samenvoegen\u2026", self.get_lang()))
        self.b_merge.clicked.connect(self.merge)
        bar.addWidget(self.b_merge)
        self.b_save = QPushButton(t("Opslaan als\u2026", self.get_lang()))
        self.b_save.clicked.connect(self.save_as)
        bar.addWidget(self.b_save)
        bar.addStretch(1)
        lay.addLayout(bar)

        bar2 = QHBoxLayout()
        bar2.setSpacing(8)
        for label, slot in [
                (t("Draai links", self.get_lang()), lambda: self.rotate(-90)),
                (t("Draai rechts", self.get_lang()), lambda: self.rotate(90)),
                (t("Pagina's verwijderen", self.get_lang()), self.delete_sel),
                (t("Splitsen\u2026", self.get_lang()), self.split)]:
            b = QPushButton(label)
            b.clicked.connect(slot)
            bar2.addWidget(b)
            if label == t("Splitsen\u2026", self.get_lang()):
                self.b_split = b
        bar2.addStretch(1)
        self.b_all = QPushButton(t("Alles selecteren", self.get_lang()))
        self.b_all.clicked.connect(lambda: self.pages.selectAll())
        bar2.addWidget(self.b_all)
        self.b_none = QPushButton(t("Niets selecteren", self.get_lang()))
        self.b_none.clicked.connect(lambda: self.pages.clearSelection())
        bar2.addWidget(self.b_none)
        lay.addLayout(bar2)

        self.pages = QListWidget()
        self.pages.setObjectName("pages")
        self.pages.setViewMode(QListWidget.ViewMode.IconMode)
        self.pages.setIconSize(QSize(120, 160))
        self.pages.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.pages.setMovement(QListWidget.Movement.Static)
        self.pages.setSpacing(10)
        self.pages.setSelectionMode(
            QAbstractItemView.SelectionMode.ExtendedSelection)
        self.pages.setUniformItemSizes(True)
        lay.addWidget(self.pages, 1)

        self.hint = QLabel(t("Open een PDF om te beginnen", self.get_lang()))
        self.hint.setObjectName("muted")
        lay.addWidget(self.hint)
        self._enable(False)

    def _enable(self, on):
        for b in (self.b_save, self.b_split, self.b_all, self.b_none):
            b.setEnabled(on)

    def open_pdf(self, path=None):
        if not path:
            path, _ = QFileDialog.getOpenFileName(
                self, t("Openen\u2026", self.get_lang()), self.get_dir(),
                t("PDF-bestanden (*.pdf)", self.get_lang()))
        if not path:
            return
        try:
            self.doc = fitz.open(path)
        except Exception as e:
            QMessageBox.warning(self, t("Kon niet openen", self.get_lang()), str(e))
            return
        self.path = path
        self.dirty = False
        self.set_dir(os.path.dirname(path))
        self._reload_pages()
        self._enable(True)

    def _reload_pages(self):
        self.pages.clear()
        if not self.doc:
            return
        for i in range(self.doc.page_count):
            it = QListWidgetItem(QIcon(thumb(self.doc, i)),
                                 "%s %d" % (t("Pagina", self.get_lang()), i + 1))
            it.setData(Qt.ItemDataRole.UserRole, i)
            it.setTextAlignment(Qt.AlignmentFlag.AlignHCenter)
            self.pages.addItem(it)
        self.hint.setText("%d %s" % (self.doc.page_count,
                                     t("pagina's", self.get_lang())
                                     if self.doc.page_count != 1
                                     else t("pagina", self.get_lang())))

    def _selected(self):
        return sorted(it.data(Qt.ItemDataRole.UserRole)
                      for it in self.pages.selectedItems())

    def rotate(self, delta):
        if not self.doc:
            return
        sel = self._selected() or list(range(self.doc.page_count))
        rotate_pages(self.doc, sel, delta)
        self.dirty = True
        self._reload_pages()

    def delete_sel(self):
        if not self.doc:
            return
        sel = self._selected()
        if not sel:
            QMessageBox.information(self, APP_NAME,
                                    t("Geen pagina's geselecteerd.", self.get_lang()))
            return
        if not delete_pages(self.doc, sel):
            return
        self.dirty = True
        self._reload_pages()

    def split(self):
        if not self.path:
            return
        out = QFileDialog.getExistingDirectory(
            self, t("Kies de map voor de losse pagina's", self.get_lang()),
            self.get_dir())
        if not out:
            return
        sel = self._selected()
        ok, res = split_pdf(self.path, out, sel if sel else None)
        if ok:
            self.status.emit(t("Klaar: %d bestanden weggeschreven.",
                               self.get_lang()) % res)
        else:
            QMessageBox.warning(self, t("Kon niet opslaan", self.get_lang()), str(res))

    def merge(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self, t("PDF's samenvoegen (kies 2 of meer)", self.get_lang()),
            self.get_dir(), t("PDF-bestanden (*.pdf)", self.get_lang()))
        if not paths or len(paths) < 2:
            return
        out, _ = QFileDialog.getSaveFileName(
            self, t("Opslaan als\u2026", self.get_lang()),
            os.path.join(self.get_dir(), "samengevoegd.pdf"),
            t("PDF-bestanden (*.pdf)", self.get_lang()))
        if not out:
            return
        if not out.lower().endswith(".pdf"):
            out += ".pdf"
        ok, res = merge_pdfs(paths, out)
        if ok:
            self.status.emit("%s %s" % (t("Opgeslagen als", self.get_lang()),
                                        os.path.basename(out)))
        else:
            QMessageBox.warning(self, t("Kon niet opslaan", self.get_lang()), str(res))

    def save_as(self):
        if not self.doc:
            return
        out, _ = QFileDialog.getSaveFileName(
            self, t("Opslaan als\u2026", self.get_lang()),
            self.path or self.get_dir(),
            t("PDF-bestanden (*.pdf)", self.get_lang()))
        if not out:
            return
        if not out.lower().endswith(".pdf"):
            out += ".pdf"
        try:
            self.doc = save_doc(self.doc, out, self.path)
            self.path = out
            self.dirty = False
            self.status.emit("%s %s" % (t("Opgeslagen als", self.get_lang()),
                                        os.path.basename(out)))
        except Exception as e:
            QMessageBox.warning(self, t("Kon niet opslaan", self.get_lang()), str(e))


# ===========================================================================
# Tabblad: Maken (tekstverwerker -> PDF, of afbeeldingen -> PDF)
# ===========================================================================
MAKE_COLORS = [("Zwart", (17, 17, 17)), ("Blauw", (20, 60, 160)),
               ("Rood", (180, 30, 30)), ("Groen", (30, 120, 40))]
MAKE_SIZES = [10, 12, 14, 16, 18, 24, 32]
LINK_COLOR = (26, 60, 160)  # gelinkte tekst: blauw + onderstreept (zoals in Maken)


def _runs_per_line(text, links):
    """Zet tekst + link-stukken (lijst van [start, eind, href]) om naar regels.
    Elke regel is een lijst van (stuk_tekst, href_of_None)."""
    n = len(text)
    hrefs = [None] * n
    for span in (links or []):
        s, e, h = span[0], span[1], span[2]
        for i in range(max(0, s), min(n, e)):
            hrefs[i] = h or None
    lines = []
    line_runs = []
    cur_text = ""
    cur_href = None
    started = False
    i = 0
    for ch in text:
        if ch == "\n":
            if started:
                line_runs.append((cur_text, cur_href))
            lines.append(line_runs)
            line_runs = []
            cur_text = ""
            cur_href = None
            started = False
            i += 1
            continue
        h = hrefs[i] if i < n else None
        if started and h == cur_href:
            cur_text += ch
        else:
            if started:
                line_runs.append((cur_text, cur_href))
            cur_text = ch
            cur_href = h
            started = True
        i += 1
    if started:
        line_runs.append((cur_text, cur_href))
    lines.append(line_runs)
    return lines

TEMPLATES = [
    ("Sjabloon\u2026", ""),
    ("Leeg", "leeg"),
    ("Standaard document", "standaard"),
    ("Zakelijke brief", "brief"),
    ("Memo / notitie", "memo"),
    ("Uitnodiging", "uitnodiging"),
]

_TMPL_HTML = {
    "leeg": "",
    "standaard": (
        "<h2>Titel van het document</h2>"
        "<p>Schrijf hier je inleiding. Vervang deze tekst door je eigen "
        "inhoud. Je kunt woorden <b>vet</b> of <i>cursief</i> maken en een "
        "afbeelding of link invoegen met de knoppen hierboven.</p>"
        "<p>Een tweede alinea met meer uitleg.</p>"),
    "brief": (
        "<p>Naam afzender<br>Straat 1<br>1234 AB Plaats</p>"
        "<p>&nbsp;</p>"
        "<p>Plaats, 1 januari 2026</p>"
        "<p>&nbsp;</p>"
        "<p><b>Betreft:</b> onderwerp van de brief</p>"
        "<p>Geachte heer/mevrouw,</p>"
        "<p>Schrijf hier de inhoud van uw brief. Vervang deze tekst door uw "
        "eigen boodschap.</p>"
        "<p>Met vriendelijke groet,</p>"
        "<p>&nbsp;</p><p>Naam</p>"),
    "memo": (
        "<h2>MEMO</h2>"
        "<p><b>Aan:</b> &nbsp;<br><b>Van:</b> &nbsp;<br>"
        "<b>Datum:</b> 1 januari 2026<br><b>Betreft:</b> &nbsp;</p>"
        "<hr>"
        "<p>Schrijf hier je notitie.</p>"),
    "uitnodiging": (
        "<h2>Uitnodiging</h2>"
        "<p>Je bent van harte uitgenodigd voor:</p>"
        "<p><b>Gelegenheid:</b> &nbsp;<br><b>Datum:</b> &nbsp;<br>"
        "<b>Tijd:</b> &nbsp;<br><b>Locatie:</b> &nbsp;</p>"
        "<p>We hopen je te zien!</p>"),
}


class MakeTab(QWidget):
    status = pyqtSignal(str)

    def __init__(self, get_lang, get_dir, set_dir):
        super().__init__()
        self.get_lang = get_lang
        self.get_dir = get_dir
        self.set_dir = set_dir
        lang = get_lang()

        lay = QVBoxLayout(self)
        lay.setContentsMargins(12, 12, 12, 12)
        lay.setSpacing(8)

        tb = QHBoxLayout()
        tb.setSpacing(6)
        self.tmpl = QComboBox()
        for label, key in TEMPLATES:
            self.tmpl.addItem(t(label, lang), key)
        self.tmpl.activated.connect(self._load_template)
        tb.addWidget(self.tmpl)
        tb.addSpacing(10)
        self.b_bold = QToolButton()
        self.b_bold.setText("B")
        self.b_bold.setCheckable(True)
        self.b_bold.setObjectName("fmtbold")
        self.b_bold.clicked.connect(self._bold)
        tb.addWidget(self.b_bold)
        self.b_ital = QToolButton()
        self.b_ital.setText("I")
        self.b_ital.setCheckable(True)
        self.b_ital.setObjectName("fmtital")
        self.b_ital.clicked.connect(self._ital)
        tb.addWidget(self.b_ital)
        self.b_und = QToolButton()
        self.b_und.setText("U")
        self.b_und.setCheckable(True)
        self.b_und.setObjectName("fmtund")
        self.b_und.clicked.connect(self._und)
        tb.addWidget(self.b_und)
        tb.addSpacing(10)
        tb.addWidget(QLabel(t("Grootte:", lang)))
        self.size = QComboBox()
        for s in MAKE_SIZES:
            self.size.addItem(str(s), s)
        self.size.setCurrentText("12")
        self.size.activated.connect(self._size)
        tb.addWidget(self.size)
        tb.addWidget(QLabel(t("Kleur:", lang)))
        self.color = QComboBox()
        for label, rgb in MAKE_COLORS:
            self.color.addItem(t(label, lang), rgb)
        self.color.activated.connect(self._color)
        tb.addWidget(self.color)
        tb.addSpacing(10)
        self.b_img = QPushButton(t("Afbeelding invoegen\u2026", lang))
        self.b_img.clicked.connect(self._insert_image)
        tb.addWidget(self.b_img)
        self.b_link = QPushButton(t("Link invoegen\u2026", lang))
        self.b_link.clicked.connect(self._insert_link)
        tb.addWidget(self.b_link)
        tb.addStretch(1)
        tb.addWidget(QLabel(t("Paginaformaat:", lang)))
        self.psize = QComboBox()
        for label, sz in PAGE_SIZES:
            self.psize.addItem(label, label)
        tb.addWidget(self.psize)
        lay.addLayout(tb)

        self.editor = QTextEdit()
        self.editor.setObjectName("paper")
        self.editor.setAcceptRichText(True)
        f = QFont("Arial")
        f.setPointSize(12)
        self.editor.setFont(f)
        self.editor.currentCharFormatChanged.connect(self._sync_buttons)
        lay.addWidget(self.editor, 1)

        bar = QHBoxLayout()
        self.b_make = QPushButton(t("PDF maken\u2026", lang))
        self.b_make.setObjectName("primary")
        self.b_make.clicked.connect(self.make_pdf)
        bar.addWidget(self.b_make)
        self.b_imgs = QPushButton(t("Afbeeldingen naar PDF\u2026", lang))
        self.b_imgs.clicked.connect(self.make_images)
        bar.addWidget(self.b_imgs)
        bar.addStretch(1)
        lay.addLayout(bar)

    # ---- opmaak ----
    def _load_template(self):
        key = self.tmpl.currentData()
        self.tmpl.setCurrentIndex(0)
        if not key:
            return
        if self.editor.toPlainText().strip():
            r = QMessageBox.question(
                self, APP_NAME,
                t("De huidige tekst vervangen door het sjabloon?", self.get_lang()))
            if r != QMessageBox.StandardButton.Yes:
                return
        self.editor.setHtml(_TMPL_HTML.get(key, ""))
        self.editor.setFocus()

    def _merge(self, fmt):
        self.editor.mergeCurrentCharFormat(fmt)
        self.editor.setFocus()

    def _bold(self):
        fmt = QTextCharFormat()
        fmt.setFontWeight(QFont.Weight.Bold if self.b_bold.isChecked()
                          else QFont.Weight.Normal)
        self._merge(fmt)

    def _ital(self):
        fmt = QTextCharFormat()
        fmt.setFontItalic(self.b_ital.isChecked())
        self._merge(fmt)

    def _und(self):
        fmt = QTextCharFormat()
        fmt.setFontUnderline(self.b_und.isChecked())
        self._merge(fmt)

    def _size(self):
        fmt = QTextCharFormat()
        fmt.setFontPointSize(float(self.size.currentData()))
        self._merge(fmt)

    def _color(self):
        rgb = self.color.currentData()
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(*rgb))
        self._merge(fmt)

    def _sync_buttons(self, _fmt=None):
        self.b_bold.setChecked(self.editor.fontWeight() >= QFont.Weight.Bold)
        self.b_ital.setChecked(self.editor.fontItalic())
        self.b_und.setChecked(self.editor.fontUnderline())

    def _insert_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self, t("Afbeelding invoegen\u2026", self.get_lang()), self.get_dir(),
            t("Afbeeldingen (*.png *.jpg *.jpeg *.bmp *.gif)", self.get_lang()))
        if not path:
            return
        img = QImage(path)
        if img.isNull():
            return
        if img.width() > 480:
            img = img.scaledToWidth(480, Qt.TransformationMode.SmoothTransformation)
        url = QUrl.fromLocalFile(path)
        self.editor.document().addResource(
            QTextDocument.ResourceType.ImageResource, url, img)
        fmt = QTextImageFormat()
        fmt.setName(url.toString())
        fmt.setWidth(img.width())
        fmt.setHeight(img.height())
        self.editor.textCursor().insertImage(fmt)
        self.editor.setFocus()

    def _insert_link(self):
        url, ok = QInputDialog.getText(
            self, t("Link invoegen\u2026", self.get_lang()), "URL (https://...):",
            text="https://")
        if not ok or not url.strip() or url.strip() == "https://":
            return
        url = url.strip()
        cur = self.editor.textCursor()
        text = cur.selectedText() or url
        fmt = QTextCharFormat()
        fmt.setAnchor(True)
        fmt.setAnchorHref(url)
        fmt.setForeground(QColor(20, 60, 200))
        fmt.setFontUnderline(True)
        cur.insertText(text, fmt)
        plain = QTextCharFormat()
        plain.setAnchor(False)
        plain.setAnchorHref("")
        plain.setForeground(QColor(17, 17, 17))
        plain.setFontUnderline(False)
        self.editor.setCurrentCharFormat(plain)
        self.editor.setFocus()

    def _pagesize(self):
        name = self.psize.currentData()
        return QPageSize(QPageSize.PageSizeId.A4 if name == "A4"
                         else QPageSize.PageSizeId.Letter)

    def make_pdf(self):
        txt = self.editor.toPlainText().strip()
        if not txt:
            QMessageBox.information(self, APP_NAME,
                                    t("Geen tekst om op te slaan.", self.get_lang()))
            return
        lines = txt.splitlines()
        first = lines[0] if lines else "document"
        out, _ = QFileDialog.getSaveFileName(
            self, t("PDF maken\u2026", self.get_lang()),
            os.path.join(self.get_dir(), safe_filename(first) + ".pdf"),
            t("PDF-bestanden (*.pdf)", self.get_lang()))
        if not out:
            return
        if not out.lower().endswith(".pdf"):
            out += ".pdf"
        try:
            writer = QPdfWriter(out)
            writer.setPageSize(self._pagesize())
            writer.setResolution(150)
            writer.setPageMargins(QMarginsF(15, 15, 15, 15),
                                  QPageLayout.Unit.Millimeter)
            doc = self.editor.document()
            pr = getattr(doc, "print", None) or getattr(doc, "print_", None)
            pr(writer)
            self.set_dir(os.path.dirname(out))
            self.status.emit(t("PDF gemaakt.", self.get_lang()))
        except Exception as e:
            QMessageBox.warning(self, t("Kon niet opslaan", self.get_lang()), str(e))

    def make_images(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self, t("Afbeeldingen naar PDF\u2026", self.get_lang()), self.get_dir(),
            t("Afbeeldingen (*.png *.jpg *.jpeg *.bmp *.gif)", self.get_lang()))
        if not paths:
            return
        out, _ = QFileDialog.getSaveFileName(
            self, t("PDF maken\u2026", self.get_lang()),
            os.path.join(self.get_dir(), "afbeeldingen.pdf"),
            t("PDF-bestanden (*.pdf)", self.get_lang()))
        if not out:
            return
        if not out.lower().endswith(".pdf"):
            out += ".pdf"
        ok, res = images_to_pdf(out, paths)
        if ok:
            self.set_dir(os.path.dirname(out))
            self.status.emit(t("PDF gemaakt.", self.get_lang()))
        else:
            QMessageBox.warning(self, t("Kon niet opslaan", self.get_lang()), str(res))


# ===========================================================================
# Tabblad: Bewerken (plaatsen, opmaken, verslepen, aanpassen, wissen)
# ===========================================================================
_EDIT_FAMILY = [("Zakelijk (Helvetica)", "helv"),
                ("Klassiek (Times)", "tiro"),
                ("Typemachine (Courier)", "cour")]
_FONTCODE = {
    ("helv", 0, 0): "helv", ("helv", 1, 0): "hebo", ("helv", 0, 1): "heit", ("helv", 1, 1): "hebi",
    ("tiro", 0, 0): "tiro", ("tiro", 1, 0): "tibo", ("tiro", 0, 1): "tiit", ("tiro", 1, 1): "tibi",
    ("cour", 0, 0): "cour", ("cour", 1, 0): "cobo", ("cour", 0, 1): "coit", ("cour", 1, 1): "cobi"}
_QFAMILY = {"helv": "Arial", "tiro": "Georgia", "cour": "Courier New"}


class PlacedItem(QLabel):
    """Sleepbaar, selecteerbaar item (tekst/afbeelding/wisvak) op de pagina."""
    def __init__(self, canvas, tab, data):
        super().__init__(canvas)
        self.tab = tab
        self.data = data
        self.setObjectName("placed")
        self.setCursor(Qt.CursorShape.SizeAllCursor)
        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self._press = None

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.RightButton:
            self.tab.remove_item(self.data)
            return
        if e.button() == Qt.MouseButton.LeftButton:
            self.tab._commit_inline()
            self.tab.select_item(self.data)
            self.setFocus()
            self._press = e.pos()
            self.raise_()

    def mouseMoveEvent(self, e):
        if self._press is not None:
            np = self.mapToParent(e.pos() - self._press)
            self.move(max(0, np.x()), max(0, np.y()))

    def mouseReleaseEvent(self, e):
        if self._press is not None:
            self._press = None
            self.tab.commit_item_pos(self)

    def mouseDoubleClickEvent(self, e):
        if self.data.get("kind") == "text":
            self.tab.edit_inline(self.data)

    def keyPressEvent(self, e):
        if e.key() in (Qt.Key.Key_Delete, Qt.Key.Key_Backspace):
            self.tab.remove_item(self.data)
        else:
            super().keyPressEvent(e)


class InlineEditor(QPlainTextEdit):
    """Meerregelig tekstvak om rechtstreeks op de pagina te typen. Groeit mee met
    de tekst. Sluit NIET bij focusverlies (zodat je de opmaak-/linkknoppen kunt
    gebruiken); afronden gaat met Esc, Ctrl+Enter, of door elders op de pagina te
    klikken."""
    def __init__(self, canvas, tab):
        super().__init__(canvas)
        self.tab = tab
        self.setObjectName("inline")
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.textChanged.connect(self.autosize)

    def autosize(self):
        fm = self.fontMetrics()
        lines = self.toPlainText().split("\n") or [""]
        if not lines:
            lines = [""]
        longest = max((fm.horizontalAdvance(ln) for ln in lines), default=0)
        w = longest + 22
        h = fm.lineSpacing() * len(lines) + 12
        # niet groter dan het canvas vanaf de huidige positie
        cw = self.parent().width() if self.parent() else w
        ch = self.parent().height() if self.parent() else h
        w = min(max(60, w), max(60, cw - self.x() - 4))
        h = min(max(fm.lineSpacing() + 12, h), max(24, ch - self.y() - 4))
        self.setFixedSize(int(w), int(h))

    def keyPressEvent(self, e):
        if e.key() == Qt.Key.Key_Escape:
            self.tab._commit_inline()
            return
        if (e.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter)
                and (e.modifiers() & Qt.KeyboardModifier.ControlModifier)):
            self.tab._commit_inline()
            return
        super().keyPressEvent(e)


class EditTab(QWidget):
    status = pyqtSignal(str)

    def __init__(self, get_lang, get_dir, set_dir):
        super().__init__()
        self.get_lang = get_lang
        self.get_dir = get_dir
        self.set_dir = set_dir
        self.doc = None
        self.path = None
        self.pno = 0
        self.zoom = 1.4
        self.mode = "select"
        self.image_path = None
        self.image_aspect = 1.0
        self.items = []
        self.selected = None
        self._binding = False
        self._rb = None
        self._rb_start = None
        self._inline = None

        lay = QVBoxLayout(self)
        lay.setContentsMargins(12, 12, 12, 12)
        lay.setSpacing(8)

        bar = QHBoxLayout()
        bar.setSpacing(8)
        self.b_open = QPushButton(t("Openen\u2026", self.get_lang()))
        self.b_open.setObjectName("primary")
        self.b_open.clicked.connect(self.open_pdf)
        bar.addWidget(self.b_open)
        self.b_prev = QToolButton()
        self.b_prev.setText("\u25c0")
        self.b_prev.clicked.connect(lambda: self.go(self.pno - 1))
        bar.addWidget(self.b_prev)
        self.page_lbl = QLabel("-")
        self.page_lbl.setObjectName("muted")
        bar.addWidget(self.page_lbl)
        self.b_next = QToolButton()
        self.b_next.setText("\u25b6")
        self.b_next.clicked.connect(lambda: self.go(self.pno + 1))
        bar.addWidget(self.b_next)
        self.b_zout = QToolButton()
        self.b_zout.setText("\u2212")
        self.b_zout.clicked.connect(lambda: self.set_zoom(self.zoom - 0.25))
        bar.addWidget(self.b_zout)
        self.b_zin = QToolButton()
        self.b_zin.setText("+")
        self.b_zin.clicked.connect(lambda: self.set_zoom(self.zoom + 0.25))
        bar.addWidget(self.b_zin)
        bar.addStretch(1)
        self.b_del = QPushButton(t("Verwijderen", self.get_lang()))
        self.b_del.clicked.connect(self.delete_selected)
        bar.addWidget(self.b_del)
        self.b_undo = QPushButton(t("Ongedaan maken", self.get_lang()))
        self.b_undo.clicked.connect(self.undo)
        bar.addWidget(self.b_undo)
        self.b_reset = QPushButton(t("Opnieuw beginnen", self.get_lang()))
        self.b_reset.clicked.connect(self.reset)
        bar.addWidget(self.b_reset)
        self.b_save = QPushButton(t("Opslaan als\u2026", self.get_lang()))
        self.b_save.clicked.connect(self.save_as)
        bar.addWidget(self.b_save)
        lay.addLayout(bar)

        modebar = QHBoxLayout()
        modebar.setSpacing(8)
        self.m_select = QPushButton(t("Selecteren", self.get_lang()))
        self.m_select.setCheckable(True)
        self.m_select.setChecked(True)
        self.m_select.clicked.connect(lambda: self.set_mode("select"))
        modebar.addWidget(self.m_select)
        self.m_text = QPushButton(t("Tekst plaatsen", self.get_lang()))
        self.m_text.setCheckable(True)
        self.m_text.clicked.connect(lambda: self.set_mode("text"))
        modebar.addWidget(self.m_text)
        self.m_img = QPushButton(t("Afbeelding plaatsen", self.get_lang()))
        self.m_img.setCheckable(True)
        self.m_img.clicked.connect(lambda: self.set_mode("image"))
        modebar.addWidget(self.m_img)
        self.m_erase = QPushButton(t("Wissen", self.get_lang()))
        self.m_erase.setCheckable(True)
        self.m_erase.clicked.connect(lambda: self.set_mode("erase"))
        modebar.addWidget(self.m_erase)
        modebar.addStretch(1)
        self.b_pick = QPushButton(t("Kies afbeelding\u2026", self.get_lang()))
        self.b_pick.clicked.connect(self.pick_image)
        modebar.addWidget(self.b_pick)
        self.img_lbl = QLabel("-")
        self.img_lbl.setObjectName("muted")
        modebar.addWidget(self.img_lbl)
        modebar.addWidget(QLabel(t("Breedte:", self.get_lang())))
        self.iwidth = QSpinBox()
        self.iwidth.setRange(20, 1000)
        self.iwidth.setValue(140)
        self.iwidth.setSuffix(" pt")
        self.iwidth.valueChanged.connect(self._on_width_changed)
        modebar.addWidget(self.iwidth)
        lay.addLayout(modebar)

        # Vaste opmaakbalk voor tekst (altijd zichtbaar)
        fmtbar = QHBoxLayout()
        fmtbar.setSpacing(6)
        fmtbar.addWidget(QLabel(t("Tekst:", self.get_lang())))
        self.b_bold = QToolButton()
        self.b_bold.setText("B")
        self.b_bold.setCheckable(True)
        self.b_bold.setObjectName("fmtbold")
        self.b_bold.clicked.connect(self._on_style_changed)
        fmtbar.addWidget(self.b_bold)
        self.b_ital = QToolButton()
        self.b_ital.setText("I")
        self.b_ital.setCheckable(True)
        self.b_ital.setObjectName("fmtital")
        self.b_ital.clicked.connect(self._on_style_changed)
        fmtbar.addWidget(self.b_ital)
        self.b_und = QToolButton()
        self.b_und.setText("U")
        self.b_und.setCheckable(True)
        self.b_und.setObjectName("fmtund")
        self.b_und.clicked.connect(self._on_style_changed)
        fmtbar.addWidget(self.b_und)
        self.b_link = QPushButton(t("Link\u2026", self.get_lang()))
        self.b_link.clicked.connect(self._set_link)
        fmtbar.addWidget(self.b_link)
        self.font = QComboBox()
        for label, code in _EDIT_FAMILY:
            self.font.addItem(t(label, self.get_lang()), code)
        self.font.activated.connect(self._on_style_changed)
        fmtbar.addWidget(self.font, 1)
        self.size = QSpinBox()
        self.size.setRange(6, 96)
        self.size.setValue(16)
        self.size.valueChanged.connect(self._on_style_changed)
        fmtbar.addWidget(self.size)
        self.color = QComboBox()
        for label, rgb in MAKE_COLORS:
            self.color.addItem(t(label, self.get_lang()), rgb)
        self.color.activated.connect(self._on_style_changed)
        fmtbar.addWidget(self.color)
        lay.addLayout(fmtbar)

        self.tip = QLabel(t("Klik om te plaatsen; sleep om te verplaatsen; "
                            "klik een item om het aan te passen; rechtsklik verwijdert.",
                            self.get_lang()))
        self.tip.setObjectName("muted")
        lay.addWidget(self.tip)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(False)
        self.scroll.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.scroll.setObjectName("pageview")
        self.canvas = QLabel()
        self.canvas.setObjectName("canvas")
        self.canvas.setText(t("Open een PDF om te beginnen", self.get_lang()))
        self.canvas.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.canvas.setMinimumSize(500, 360)
        self.canvas.mousePressEvent = self._canvas_press
        self.canvas.mouseMoveEvent = self._canvas_move
        self.canvas.mouseReleaseEvent = self._canvas_release
        self.scroll.setWidget(self.canvas)
        lay.addWidget(self.scroll, 1)

        self._enable(False)
        self._update_tip()

    def _enable(self, on):
        for w in (self.b_prev, self.b_next, self.b_zin, self.b_zout, self.b_undo,
                  self.b_reset, self.b_save, self.b_del):
            w.setEnabled(on)

    def set_mode(self, mode):
        self._commit_inline()
        self.mode = mode
        self.m_select.setChecked(mode == "select")
        self.m_text.setChecked(mode == "text")
        self.m_img.setChecked(mode == "image")
        self.m_erase.setChecked(mode == "erase")
        self._update_tip()

    def _update_tip(self):
        tips = {
            "select": t("Klik een item om het te selecteren, sleep om te "
                        "verplaatsen, dubbelklik tekst om te wijzigen.", self.get_lang()),
            "text": t("Klik op de pagina en typ. Opmaak en link kies je in de "
                      "balk hierboven.", self.get_lang()),
            "image": t("Kies een afbeelding en klik op de pagina.", self.get_lang()),
            "erase": t("Sleep een vak over wat je wilt weghalen.", self.get_lang()),
        }
        self.tip.setText(tips.get(self.mode, ""))

    # ---- openen / navigatie ----
    def open_pdf(self, path=None):
        if not path:
            path, _ = QFileDialog.getOpenFileName(
                self, t("Openen\u2026", self.get_lang()), self.get_dir(),
                t("PDF-bestanden (*.pdf)", self.get_lang()))
        if not path:
            return
        try:
            doc = fitz.open(path)
        except Exception as e:
            QMessageBox.warning(self, t("Kon niet openen", self.get_lang()), str(e))
            return
        self._clear_items()
        self.doc = doc
        self.path = path
        self.pno = 0
        self.set_dir(os.path.dirname(path))
        self._enable(True)
        self._render()

    def go(self, pno):
        if not self.doc:
            return
        self.pno = max(0, min(self.doc.page_count - 1, pno))
        self._render()

    def set_zoom(self, z):
        self.zoom = max(0.5, min(4.0, round(z, 2)))
        if self.doc:
            self._render()

    def _render(self):
        if not self.doc:
            return
        img, w, h = render_page(self.doc, self.pno, self.zoom)
        self.canvas.setPixmap(QPixmap.fromImage(img))
        self.canvas.resize(w, h)
        self.page_lbl.setText("%s %d %s %d" % (
            t("Pagina", self.get_lang()), self.pno + 1,
            t("van", self.get_lang()), self.doc.page_count))
        self._end_inline()
        self._layout_items()

    def pick_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self, t("Kies afbeelding\u2026", self.get_lang()), self.get_dir(),
            t("Afbeeldingen (*.png *.jpg *.jpeg *.bmp *.gif)", self.get_lang()))
        if path:
            pm = QPixmap(path)
            self.image_path = path
            self.image_aspect = (pm.height() / pm.width()) if pm.width() else 1.0
            self.img_lbl.setText(os.path.basename(path))
            self.set_mode("image")

    # ---- plaatsen via klik / wis-vak via slepen ----
    def _canvas_press(self, ev):
        if not self.doc:
            return
        # typt er iemand? Dan rondt deze klik het typen af en blijft het vak
        # geselecteerd (zodat opmaak/link er meteen op werken). Niet deselecteren.
        if self._inline is not None:
            self._commit_inline()
            return
        if ev.button() != Qt.MouseButton.LeftButton:
            # rechtsklik op leeg canvas: alleen de selectie opheffen
            self.select_item(None)
            return
        if self.mode == "select":
            self.select_item(None)
            return
        if self.mode == "erase":
            self._rb_start = ev.pos()
            self._rb = QFrame(self.canvas)
            self._rb.setObjectName("rubber")
            self._rb.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
            self._rb.setGeometry(QRect(ev.pos(), ev.pos()))
            self._rb.show()
            return
        x = ev.pos().x() / self.zoom
        y = ev.pos().y() / self.zoom
        self.select_item(None)
        if self.mode == "text":
            data = {"kind": "text", "page": self.pno, "x": x, "y": y,
                    "text": "", "font": self.font.currentData(),
                    "size": self.size.value(), "color": self.color.currentData(),
                    "bold": self.b_bold.isChecked(), "italic": self.b_ital.isChecked(),
                    "underline": self.b_und.isChecked(), "links": []}
            self.items.append(data)
            self._make_widget(data)
            self.mode = "select"
            self.m_select.setChecked(True)
            self.m_text.setChecked(False)
            self.select_item(data)
            # meteen typen op de pagina
            self.edit_inline(data)
            return
        else:
            if not self.image_path:
                QMessageBox.information(self, APP_NAME,
                                        t("Kies eerst een afbeelding.", self.get_lang()))
                return
            data = {"kind": "image", "page": self.pno, "x": x, "y": y,
                    "w": self.iwidth.value(), "aspect": self.image_aspect,
                    "imgpath": self.image_path}
        self.items.append(data)
        self._make_widget(data)
        # een item per klik: meteen terug naar Selecteren zodat je kunt slepen/wijzigen
        self.mode = "select"
        self.m_select.setChecked(True)
        self.m_text.setChecked(False)
        self.m_img.setChecked(False)
        self.select_item(data)

    def _canvas_move(self, ev):
        if self._rb is not None and self._rb_start is not None:
            self._rb.setGeometry(QRect(self._rb_start, ev.pos()).normalized())

    def _canvas_release(self, ev):
        if self._rb is None:
            return
        g = QRect(self._rb_start, ev.pos()).normalized()
        self._rb.setParent(None)
        self._rb.deleteLater()
        self._rb = None
        self._rb_start = None
        if g.width() < 6 or g.height() < 6:
            return
        z = self.zoom
        data = {"kind": "erase", "page": self.pno, "x": g.x() / z, "y": g.y() / z,
                "w": g.width() / z, "h": g.height() / z}
        self.items.append(data)
        self._make_widget(data)
        self.mode = "select"
        self.m_select.setChecked(True)
        self.m_erase.setChecked(False)
        self.select_item(data)

    # ---- items / widgets ----
    def _make_widget(self, data):
        w = PlacedItem(self.canvas, self, data)
        data["widget"] = w
        w.show()
        self._refresh_widget(data)

    def _refresh_widget(self, data):
        w = data.get("widget")
        if not w:
            return
        z = self.zoom
        sel = (data is self.selected)
        if data["kind"] == "text":
            fam = _QFAMILY.get(data["font"], "Arial")
            f = QFont(fam)
            f.setBold(bool(data.get("bold")))
            f.setItalic(bool(data.get("italic")))
            f.setUnderline(bool(data.get("underline")))
            f.setPixelSize(max(6, int(data["size"] * z)))
            w.setFont(f)
            base = data["color"]
            base_und = bool(data.get("underline"))
            lines = _runs_per_line(data["text"], data.get("links"))

            def esc(s):
                return (s.replace("&", "&amp;").replace("<", "&lt;")
                        .replace(">", "&gt;").replace(" ", "&nbsp;"))
            html_lines = []
            for line_runs in lines:
                parts = []
                for seg, href in line_runs:
                    if href:
                        parts.append('<span style="color:#1a3ca0;'
                                     'text-decoration:underline">%s</span>' % esc(seg))
                    else:
                        st = "color:rgb(%d,%d,%d)" % (base[0], base[1], base[2])
                        if base_und:
                            st += ";text-decoration:underline"
                        parts.append('<span style="%s">%s</span>' % (st, esc(seg)))
                html_lines.append("".join(parts) or "&nbsp;")
            w.setText("<br>".join(html_lines))
            border = "2px solid %s" % ACCENT if sel else "1px dashed rgba(111,163,214,90)"
            w.setStyleSheet("background: rgba(111,163,214,30); border: %s;" % border)
            w.adjustSize()
        elif data["kind"] == "image":
            pm = QPixmap(data["imgpath"])
            ww = max(8, int(data["w"] * z))
            hh = max(8, int(data["w"] * data["aspect"] * z))
            w.setPixmap(pm.scaled(ww, hh, Qt.AspectRatioMode.IgnoreAspectRatio,
                                  Qt.TransformationMode.SmoothTransformation))
            w.setFixedSize(ww, hh)
            border = "2px solid %s" % ACCENT if sel else "1px dashed rgba(111,163,214,160)"
            w.setStyleSheet("border: %s;" % border)
        else:  # erase
            ww = max(8, int(data["w"] * z))
            hh = max(8, int(data["h"] * z))
            w.setFixedSize(ww, hh)
            w.setText("")
            # dekkend wit: inhoud verdwijnt meteen zichtbaar (zoals na opslaan).
            # rand alleen tonen als het vak geselecteerd is, zodat er geen randje
            # in beeld blijft staan.
            if sel:
                w.setStyleSheet("background: #ffffff; border: 2px dashed %s;" % ACCENT)
            else:
                w.setStyleSheet("background: #ffffff; border: none;")
        w.move(int(data["x"] * z), int(data["y"] * z))

    def _layout_items(self):
        for data in self.items:
            w = data.get("widget")
            if not w:
                continue
            if data["page"] == self.pno:
                self._refresh_widget(data)
                w.show()
                w.raise_()
            else:
                w.hide()

    def commit_item_pos(self, widget):
        data = widget.data
        data["x"] = widget.x() / self.zoom
        data["y"] = widget.y() / self.zoom

    # ---- selectie + aanpassen ----
    def _combo_to(self, combo, value):
        for i in range(combo.count()):
            if combo.itemData(i) == value:
                combo.setCurrentIndex(i)
                return

    def select_item(self, data):
        self.selected = data
        if data is not None:
            self._binding = True
            if data["kind"] == "text":
                self._combo_to(self.font, data.get("font", "helv"))
                self.size.setValue(int(data.get("size", 16)))
                self._combo_to(self.color, data.get("color", (17, 17, 17)))
                self.b_bold.setChecked(bool(data.get("bold")))
                self.b_ital.setChecked(bool(data.get("italic")))
                self.b_und.setChecked(bool(data.get("underline")))
                self._update_link_btn(data)
            elif data["kind"] == "image":
                self.iwidth.setValue(int(data.get("w", 140)))
            self._binding = False
        else:
            self._update_link_btn(None)
        self._layout_items()

    def _update_link_btn(self, data):
        has = bool(data and data.get("kind") == "text" and data.get("links"))
        self.b_link.setText(t("Link \u2713", self.get_lang()) if has
                            else t("Link\u2026", self.get_lang()))

    def _link_fmt(self, url, base_color, base_und):
        fmt = QTextCharFormat()
        if url:
            fmt.setAnchor(True)
            fmt.setAnchorHref(url)
            fmt.setForeground(QColor(LINK_COLOR[0], LINK_COLOR[1], LINK_COLOR[2]))
            fmt.setFontUnderline(True)
        else:
            fmt.setAnchor(False)
            fmt.setAnchorHref("")
            fmt.setForeground(QColor(base_color[0], base_color[1], base_color[2]))
            fmt.setFontUnderline(bool(base_und))
        return fmt

    def _extract_links(self, ed):
        """Lees uit het tekstvak welke teken-stukken een link hebben."""
        links = []
        doc = ed.document()
        block = doc.begin()
        while block.isValid():
            it = block.begin()
            while not it.atEnd():
                frag = it.fragment()
                if frag.isValid():
                    href = frag.charFormat().anchorHref()
                    if href:
                        s = frag.position()
                        links.append([s, s + len(frag.text()), href])
                it += 1
            block = block.next()
        links.sort()
        merged = []
        for s, e, h in links:
            if merged and merged[-1][2] == h and merged[-1][1] == s:
                merged[-1][1] = e
            else:
                merged.append([s, e, h])
        return merged

    def _set_link(self):
        # 1) Typend in een tekstvak:
        #    - heb je tekst GESELECTEERD -> die selectie wordt de link
        #    - niets geselecteerd -> de URL komt als klikbaar linkje op de cursor
        if self._inline:
            ed, target = self._inline
            cur = ed.textCursor()
            prefill = cur.charFormat().anchorHref() or "https://"
            url, ok = QInputDialog.getText(
                self, t("Link\u2026", self.get_lang()),
                t("URL (https://...):", self.get_lang()), text=prefill)
            if not ok:
                return
            url = url.strip()
            if url == "https://":
                url = ""
            if cur.hasSelection():
                cur.mergeCharFormat(
                    self._link_fmt(url, target["color"], target.get("underline")))
            elif url:
                cur.insertText(
                    url, self._link_fmt(url, target["color"], target.get("underline")))
                # daarna weer normaal verder typen
                ed.setCurrentCharFormat(
                    self._link_fmt("", target["color"], target.get("underline")))
            target["links"] = self._extract_links(ed)
            self._update_link_btn(target)
            ed.autosize()
            ed.setFocus()
            self.status.emit(t("Link toegevoegd.", self.get_lang()) if url
                             else t("Link verwijderd.", self.get_lang()))
            return
        # 2) Een geselecteerd (niet-typend) tekstvak: voeg de URL als klikbaar
        #    linkje achter de tekst toe (niet de hele tekst tot link maken)
        if self.selected and self.selected.get("kind") == "text":
            target = self.selected
            url, ok = QInputDialog.getText(
                self, t("Link\u2026", self.get_lang()),
                t("URL (https://...):", self.get_lang()), text="https://")
            if not ok or not url.strip() or url.strip() == "https://":
                return
            url = url.strip()
            txt = target.get("text", "")
            sep = "" if (not txt or txt.endswith((" ", "\n"))) else " "
            start = len(txt) + len(sep)
            target["text"] = txt + sep + url
            target.setdefault("links", []).append([start, start + len(url), url])
            self._update_link_btn(target)
            self._refresh_widget(target)
            self.status.emit(t("Link toegevoegd.", self.get_lang()))
            return
        # 3) Niets actief -> een LOS, sleepbaar link-tekstje maken
        if not self.doc:
            return
        url, ok = QInputDialog.getText(
            self, t("Link\u2026", self.get_lang()),
            t("URL (https://...):", self.get_lang()), text="https://")
        if not ok or not url.strip() or url.strip() == "https://":
            return
        url = url.strip()
        page = self.doc[self.pno]
        pw = float(page.rect.width) or 595.0
        ph = float(page.rect.height) or 842.0
        n = len([d for d in self.items if d.get("page") == self.pno])
        x = pw * 0.16 + (n % 6) * 12
        y = ph * 0.2 + (n % 6) * 14
        data = {"kind": "text", "page": self.pno, "x": x, "y": y,
                "text": url, "font": self.font.currentData(),
                "size": self.size.value(), "color": self.color.currentData(),
                "bold": self.b_bold.isChecked(), "italic": self.b_ital.isChecked(),
                "underline": self.b_und.isChecked(),
                "links": [[0, len(url), url]]}
        self.items.append(data)
        self._make_widget(data)
        self.select_item(data)
        self.status.emit(t("Link toegevoegd. Sleep hem naar de juiste plek.",
                           self.get_lang()))

    def edit_inline(self, data):
        """Typ/bewerk de tekst rechtstreeks op de pagina (meerdere regels)."""
        if data.get("kind") != "text":
            return
        self._end_inline()
        self.select_item(data)
        ed = InlineEditor(self.canvas, self)
        ed.move(data["widget"].x(), data["widget"].y())
        ed.setPlainText(data.get("text", ""))
        self._apply_inline_format(ed, data)
        ed.autosize()
        ed.show()
        ed.setFocus()
        ed.selectAll()
        self._inline = (ed, data)

    def _apply_inline_format(self, ed, data):
        """Past lettertype + vet/cursief/onderstreept/kleur toe in het tekstvak,
        en daarna de link-stukken (blauw + onderstreept) op de juiste plekken."""
        fam = _QFAMILY.get(data["font"], "Arial")
        f = QFont(fam)
        f.setPixelSize(max(8, int(data["size"] * self.zoom)))
        ed.setFont(f)
        fmt = QTextCharFormat()
        fmt.setFontWeight(QFont.Weight.Bold if data.get("bold") else QFont.Weight.Normal)
        fmt.setFontItalic(bool(data.get("italic")))
        fmt.setFontUnderline(bool(data.get("underline")))
        c = data["color"]
        fmt.setForeground(QColor(c[0], c[1], c[2]))
        cur = ed.textCursor()
        pos = cur.position()
        cur.select(QTextCursor.SelectionType.Document)
        cur.mergeCharFormat(fmt)
        # link-stukken er overheen
        for span in data.get("links", []):
            s, e, h = span[0], span[1], span[2]
            lc = ed.textCursor()
            lc.setPosition(s)
            lc.setPosition(e, QTextCursor.MoveMode.KeepAnchor)
            lc.mergeCharFormat(self._link_fmt(h, data["color"], data.get("underline")))
        cur.clearSelection()
        cur.setPosition(min(pos, len(ed.toPlainText())))
        ed.setTextCursor(cur)

    def _commit_inline(self):
        if not self._inline:
            return
        ed, data = self._inline
        self._inline = None
        data["text"] = ed.toPlainText().rstrip("\n")
        data["links"] = self._extract_links(ed)
        ed.setParent(None)
        ed.deleteLater()
        if not data["text"].strip():
            # leeg gelaten -> verwijder het lege tekstvak
            self.remove_item(data)
        else:
            # vak blijft geselecteerd, zodat opmaak/link er meteen op werken
            self.select_item(data)

    def _end_inline(self):
        # netjes afronden (tekst bewaren) als er nog een vak open staat
        if self._inline:
            self._commit_inline()

    def _on_style_changed(self, *_):
        if self._binding:
            return
        # doel = het vak dat je aan het typen bent, anders het geselecteerde tekstitem
        target = None
        if self._inline:
            target = self._inline[1]
        elif self.selected and self.selected.get("kind") == "text":
            target = self.selected
        if target and target.get("kind") == "text":
            target.update({
                "font": self.font.currentData(), "size": self.size.value(),
                "color": self.color.currentData(), "bold": self.b_bold.isChecked(),
                "italic": self.b_ital.isChecked(), "underline": self.b_und.isChecked()})
            self._refresh_widget(target)
            if self._inline and self._inline[1] is target:
                # opmaak meteen zichtbaar maken in het open tekstvak
                ed = self._inline[0]
                self._apply_inline_format(ed, target)
                ed.autosize()
                ed.setFocus()

    def _on_width_changed(self, *_):
        if self._binding:
            return
        if self.selected and self.selected.get("kind") == "image":
            self.selected["w"] = self.iwidth.value()
            self._refresh_widget(self.selected)

    def delete_selected(self):
        if self._inline:
            item = self._inline[1]
            self._inline[0].setParent(None)
            self._inline[0].deleteLater()
            self._inline = None
            self.remove_item(item)
            return
        if self.selected:
            self.remove_item(self.selected)

    def remove_item(self, data):
        if self._inline and self._inline[1] is data:
            self._inline[0].setParent(None)
            self._inline[0].deleteLater()
            self._inline = None
        if data is self.selected:
            self.selected = None
        if data in self.items:
            self.items.remove(data)
        w = data.get("widget")
        if w:
            w.setParent(None)
            w.deleteLater()

    def _clear_items(self):
        self._end_inline()
        for data in self.items:
            w = data.get("widget")
            if w:
                w.setParent(None)
                w.deleteLater()
        self.items = []
        self.selected = None

    def undo(self):
        self._commit_inline()
        if self.items:
            self.remove_item(self.items[-1])

    def reset(self):
        self._clear_items()

    # ---- opslaan: alles in een verse kopie bakken ----
    def save_as(self):
        if not self.doc:
            return
        self._commit_inline()
        if not self.items:
            QMessageBox.information(self, APP_NAME,
                                    t("Er is nog niets geplaatst.", self.get_lang()))
            return
        out, _ = QFileDialog.getSaveFileName(
            self, t("Opslaan als\u2026", self.get_lang()),
            self.path or self.get_dir(),
            t("PDF-bestanden (*.pdf)", self.get_lang()))
        if not out:
            return
        if not out.lower().endswith(".pdf"):
            out += ".pdf"
        try:
            fresh = fitz.open(self.path)
            pages = {}
            for data in self.items:
                pages.setdefault(data["page"], []).append(data)
            for pno, items in pages.items():
                page = fresh[pno]
                # 1) wissen (redacties) eerst
                erased = [d for d in items if d["kind"] == "erase"]
                for d in erased:
                    page.add_redact_annot(
                        fitz.Rect(d["x"], d["y"], d["x"] + d["w"], d["y"] + d["h"]),
                        fill=(1, 1, 1), cross_out=False)
                if erased:
                    page.apply_redactions()
                    # schone witte rechthoek (zonder rand) over het vak, iets ruimer,
                    # zodat er geen dun randje van de redactie zichtbaar blijft
                    for d in erased:
                        page.draw_rect(
                            fitz.Rect(d["x"] - 0.75, d["y"] - 0.75,
                                      d["x"] + d["w"] + 0.75, d["y"] + d["h"] + 0.75),
                            color=None, fill=(1, 1, 1))
                # 2) daarna tekst/afbeeldingen erop
                for d in items:
                    if d["kind"] == "text":
                        code = _FONTCODE.get(
                            (d["font"], int(bool(d.get("bold"))),
                             int(bool(d.get("italic")))), "helv")
                        basecol = tuple(c / 255.0 for c in d["color"])
                        linkcol = tuple(c / 255.0 for c in LINK_COLOR)
                        base_und = bool(d.get("underline"))
                        size = d["size"]
                        lh = size * 1.4
                        lines = _runs_per_line(d["text"], d.get("links"))
                        for i, line_runs in enumerate(lines):
                            ly = d["y"] + size * 0.8 + i * lh
                            uy = d["y"] + size * 0.95 + i * lh
                            cx = d["x"]
                            for seg, href in line_runs:
                                if not seg:
                                    continue
                                col = linkcol if href else basecol
                                page.insert_text((cx, ly), seg, fontname=code,
                                                 fontsize=size, color=col)
                                segw = fitz.get_text_length(seg, fontname=code,
                                                            fontsize=size)
                                if href or base_und:
                                    page.draw_line((cx, uy), (cx + segw, uy),
                                                   color=col, width=max(0.4, size * 0.05))
                                if href:
                                    page.insert_link({
                                        "kind": fitz.LINK_URI,
                                        "from": fitz.Rect(cx, d["y"] + i * lh,
                                                          cx + segw, d["y"] + (i + 1) * lh),
                                        "uri": href})
                                cx += segw
                    elif d["kind"] == "image":
                        rect = fitz.Rect(d["x"], d["y"], d["x"] + d["w"],
                                         d["y"] + d["w"] * d["aspect"])
                        page.insert_image(rect, filename=d["imgpath"])
            saved = save_doc(fresh, out, self.path)
            try:
                saved.close()
            except Exception:
                pass
            try:
                self.doc.close()
            except Exception:
                pass
            self._clear_items()
            self.doc = fitz.open(out)
            self.path = out
            self._render()
            self.status.emit("%s %s" % (t("Opgeslagen als", self.get_lang()),
                                        os.path.basename(out)))
        except Exception as e:
            QMessageBox.warning(self, t("Kon niet opslaan", self.get_lang()), str(e))



# ===========================================================================
# Tabblad 2: Ondertekenen
# ===========================================================================
SIGN_FONTS = [
    ("Sierlijk (Times cursief)", "tiit"),
    ("Sierlijk vet (Times)", "tibi"),
    ("Zakelijk (Helvetica)", "helv"),
    ("Typemachine (Courier)", "cour"),
]
SIGN_COLORS = [("Zwart", (0, 0, 0)), ("Blauw", (0.10, 0.20, 0.55))]


class SignTab(QWidget):
    status = pyqtSignal(str)

    def __init__(self, get_lang, get_dir, set_dir):
        super().__init__()
        self.get_lang = get_lang
        self.get_dir = get_dir
        self.set_dir = set_dir
        self.doc = None
        self.path = None
        self.pno = 0
        self.zoom = 1.4
        self.place = None  # (x_pdf, y_pdf)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(12, 12, 12, 12)
        lay.setSpacing(8)

        bar = QHBoxLayout()
        bar.setSpacing(8)
        self.b_open = QPushButton(t("Openen\u2026", self.get_lang()))
        self.b_open.setObjectName("primary")
        self.b_open.clicked.connect(self.open_pdf)
        bar.addWidget(self.b_open)
        self.b_prev = QToolButton()
        self.b_prev.setText("\u25c0")
        self.b_prev.clicked.connect(lambda: self.go(self.pno - 1))
        bar.addWidget(self.b_prev)
        self.page_lbl = QLabel("-")
        self.page_lbl.setObjectName("muted")
        bar.addWidget(self.page_lbl)
        self.b_next = QToolButton()
        self.b_next.setText("\u25b6")
        self.b_next.clicked.connect(lambda: self.go(self.pno + 1))
        bar.addWidget(self.b_next)
        bar.addStretch(1)
        self.b_sign = QPushButton(t("Onderteken en opslaan als\u2026", self.get_lang()))
        self.b_sign.clicked.connect(self.do_sign)
        bar.addWidget(self.b_sign)
        lay.addLayout(bar)

        form = QHBoxLayout()
        form.setSpacing(8)
        form.addWidget(QLabel(t("Naam:", self.get_lang())))
        self.name = QLineEdit()
        self.name.textChanged.connect(self._update_preview)
        form.addWidget(self.name, 2)
        form.addWidget(QLabel(t("Lettertype:", self.get_lang())))
        self.font = QComboBox()
        for label, code in SIGN_FONTS:
            self.font.addItem(t(label, self.get_lang()), code)
        self.font.currentIndexChanged.connect(self._update_preview)
        form.addWidget(self.font, 1)
        form.addWidget(QLabel(t("Grootte:", self.get_lang())))
        self.size = QSpinBox()
        self.size.setRange(8, 96)
        self.size.setValue(28)
        self.size.valueChanged.connect(self._update_preview)
        form.addWidget(self.size)
        form.addWidget(QLabel(t("Kleur:", self.get_lang())))
        self.color = QComboBox()
        for label, rgb in SIGN_COLORS:
            self.color.addItem(t(label, self.get_lang()), rgb)
        self.color.currentIndexChanged.connect(self._update_preview)
        form.addWidget(self.color)
        lay.addLayout(form)

        self.tip = QLabel(t("Klik op de pagina om je handtekening te plaatsen.",
                            self.get_lang()))
        self.tip.setObjectName("muted")
        lay.addWidget(self.tip)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(False)
        self.scroll.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.scroll.setObjectName("pageview")
        self.canvas = QLabel()
        self.canvas.setObjectName("canvas")
        self.canvas.setText(t("Open een PDF om te beginnen", self.get_lang()))
        self.canvas.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.canvas.setMinimumSize(500, 360)
        self.canvas.mousePressEvent = self._canvas_click
        self.scroll.setWidget(self.canvas)
        lay.addWidget(self.scroll, 1)

        self.preview = QLabel(self.canvas)
        self.preview.setObjectName("sigpreview")
        self.preview.setVisible(False)

        self._enable(False)

    def _enable(self, on):
        for w in (self.b_prev, self.b_next, self.b_sign):
            w.setEnabled(on)

    def open_pdf(self, path=None):
        if not path:
            path, _ = QFileDialog.getOpenFileName(
                self, t("Openen\u2026", self.get_lang()), self.get_dir(),
                t("PDF-bestanden (*.pdf)", self.get_lang()))
        if not path:
            return
        try:
            self.doc = fitz.open(path)
        except Exception as e:
            QMessageBox.warning(self, t("Kon niet openen", self.get_lang()), str(e))
            return
        self.path = path
        self.pno = 0
        self.place = None
        self.set_dir(os.path.dirname(path))
        self._enable(True)
        self._render()

    def go(self, pno):
        if not self.doc:
            return
        self.pno = max(0, min(self.doc.page_count - 1, pno))
        self.place = None
        self.preview.setVisible(False)
        self._render()

    def _render(self):
        if not self.doc:
            return
        img, w, h = render_page(self.doc, self.pno, self.zoom)
        self.canvas.setPixmap(QPixmap.fromImage(img))
        self.canvas.resize(w, h)
        self.page_lbl.setText("%s %d %s %d" % (
            t("Pagina", self.get_lang()), self.pno + 1,
            t("van", self.get_lang()), self.doc.page_count))

    def _canvas_click(self, ev):
        if not self.doc:
            return
        x = ev.pos().x()
        y = ev.pos().y()
        self.place = (x / self.zoom, y / self.zoom)
        self._update_preview()

    def _update_preview(self):
        if not self.doc or self.place is None or not self.name.text().strip():
            self.preview.setVisible(False)
            return
        code = self.font.currentData()
        size = self.size.value()
        rgb = self.color.currentData()
        qfont = {"tiit": ("Georgia", True, False), "tibi": ("Georgia", True, True),
                 "helv": ("Arial", False, False), "cour": ("Courier New", False, False)
                 }.get(code, ("Georgia", True, False))
        from PyQt6.QtGui import QFont
        f = QFont(qfont[0])
        f.setItalic(qfont[1])
        f.setBold(qfont[2])
        f.setPixelSize(int(size * self.zoom))
        self.preview.setFont(f)
        self.preview.setText(self.name.text())
        col = QColor(int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255))
        self.preview.setStyleSheet("color: rgb(%d,%d,%d); background: transparent;"
                                   % (col.red(), col.green(), col.blue()))
        self.preview.adjustSize()
        px = int(self.place[0] * self.zoom)
        py = int(self.place[1] * self.zoom)
        self.preview.move(px, py)
        self.preview.setVisible(True)
        self.preview.raise_()

    def do_sign(self):
        if not self.doc:
            return
        if not self.name.text().strip():
            QMessageBox.information(self, APP_NAME,
                                    t("Typ eerst je naam.", self.get_lang()))
            return
        if self.place is None:
            QMessageBox.information(self, APP_NAME,
                                    t("Plaats eerst je handtekening (klik op de pagina).",
                                      self.get_lang()))
            return
        out, _ = QFileDialog.getSaveFileName(
            self, t("Onderteken en opslaan als\u2026", self.get_lang()),
            self.path or self.get_dir(),
            t("PDF-bestanden (*.pdf)", self.get_lang()))
        if not out:
            return
        if not out.lower().endswith(".pdf"):
            out += ".pdf"
        code = self.font.currentData()
        size = self.size.value()
        rgb = self.color.currentData()
        # baseline iets onder het klikpunt zodat de tekst staat waar je klikte
        point = (self.place[0], self.place[1] + size * 0.8)
        try:
            sign_text(self.doc, self.pno, point, self.name.text(), code, size, rgb)
            self.doc = save_doc(self.doc, out, self.path)
            # schoon heropenen vanaf het origineel zodat je door kunt
            try:
                self.doc.close()
            except Exception:
                pass
            self.doc = fitz.open(self.path)
            self.place = None
            self.preview.setVisible(False)
            self._render()
            self.status.emit(t("Ondertekend en opgeslagen.", self.get_lang()))
        except Exception as e:
            QMessageBox.warning(self, t("Kon niet opslaan", self.get_lang()), str(e))


# ---------------------------------------------------------------------------
# Snelgids / Instellingen
# ---------------------------------------------------------------------------
GUIDE_NL = """DravePDF - Snelgids

DravePDF heeft vier tabbladen: PDF-gereedschap, Maken, Bewerken en Ondertekenen.

Maken (tekstverwerker)
- Kies eventueel een Sjabloon (standaard, zakelijke brief, memo, uitnodiging)
  om snel te beginnen.
- Typ je tekst en maak op met B (vet), I (cursief), U (onderstrepen), kleur en
  lettergrootte. Voeg een afbeelding of een link in. Kies het paginaformaat.
- 'PDF maken' slaat alles op als PDF (de naam wordt voorgesteld op basis van je
  eerste regel). 'Afbeeldingen naar PDF' maakt van losse afbeeldingen pagina's.

PDF-gereedschap
- 'Openen' toont de pagina's als miniaturen. Selecteer pagina's (Ctrl/Shift
  voor meerdere) en gebruik:
  - 'Draai links/rechts' om geselecteerde pagina's te draaien.
  - 'Pagina's verwijderen' om ze weg te halen.
  - 'Splitsen' schrijft elke (geselecteerde) pagina als los PDF-bestand.
- 'Samenvoegen' voegt meerdere PDF's samen tot een nieuw bestand.
- 'Opslaan als' bewaart het resultaat als nieuwe PDF.

Bewerken (plaatsen, opmaken, aanpassen, wissen)
Er zijn vier knoppen: Selecteren, Tekst plaatsen, Afbeelding plaatsen, Wissen.
- Selecteren (standaard): klik een item om het te kiezen, SLEEP om te
  verplaatsen, DUBBELKLIK op tekst om die ter plekke te wijzigen. 'Verwijderen'
  of rechtsklik haalt een item weg (of Delete-toets).
- Onderaan staat een vaste opmaakbalk voor tekst (altijd zichtbaar): B (vet),
  I (cursief), U (onderstrepen), de knop 'Link...', lettertype, grootte en kleur.
- Link toevoegen werkt net als in Maken:
  * Heb je een stuk tekst GESELECTEERD -> dat stuk wordt de link (blauw +
    onderstreept), de rest blijft zwart.
  * Niets geselecteerd terwijl je typt -> de URL komt als klikbaar linkje op de
    cursor in het tekstvak.
  * Niets actief -> er verschijnt een los link-tekstje dat je naar de juiste plek
    sleept.
  Gelinkte tekst is klikbaar in de PDF. Selecteer een gelinkt stuk en klik
  'Link...' met een lege URL om de link weer weg te halen.
- Tekst plaatsen: klik op de pagina; er verschijnt EEN tekstvak waar je meteen
  in typt (meerdere regels mag, met Enter). Het vak groeit mee met je tekst.
  Opmaak en link pas je toe met de balk TERWIJL je typt (het vak blijft open en
  je ziet vet/cursief/onderstrepen meteen). Klik ergens anders of druk Esc /
  Ctrl+Enter om af te ronden.
- Dubbelklik op een tekstvak om de tekst opnieuw te bewerken.
- Afbeelding plaatsen: kies een afbeelding, stel de breedte in, klik een keer.
- Wissen: sleep een vak over bestaande tekst of een afbeelding om die weg te
  halen. Het wisvak kun je daarna nog verslepen.
- Een geselecteerd item pas je aan met de balk (tekst, opmaak, kleur, breedte,
  link). 'Ongedaan maken'/'Opnieuw beginnen' en zoom met - en +.
- 'Opslaan als' bakt alles in een nieuwe PDF.

Ondertekenen
- Open een PDF, blader naar de juiste pagina.
- Typ je naam, kies een lettertype, grootte en kleur.
- Klik op de pagina waar je handtekening moet komen (je ziet een voorbeeld).
- 'Onderteken en opslaan als' maakt een ondertekende kopie.

DravePDF werkt volledig offline en op je eigen bestanden.

Vragen of een tip? service@dravenlock.nl
"""

GUIDE_EN = """DravePDF - Quick guide

DravePDF has four tabs: PDF tools, Create, Edit and Sign.

Create (word processor)
- Optionally pick a Template (standard, business letter, memo, invitation).
- Type your text and format it with B (bold), I (italic), U (underline),
  colour and size. Insert an image or a link. Pick the page size.
- 'Create PDF' saves it as a PDF (the name is suggested from your first line).
  'Images to PDF' turns separate images into pages.

PDF tools
- 'Open' shows the pages as thumbnails. Select pages (Ctrl/Shift for more)
  and use:
  - 'Rotate left/right' to rotate selected pages.
  - 'Delete pages' to remove them.
  - 'Split' writes each (selected) page as a separate PDF.
- 'Merge' combines several PDFs into one new file.
- 'Save as' stores the result as a new PDF.

Edit (place, format, adjust, erase)
Four buttons: Select, Place text, Place image, Erase.
- Select (default): click an item to select it, DRAG to move, DOUBLE-CLICK text
  to edit it in place. 'Delete' or right-click removes an item.
- A fixed formatting bar for text is always visible at the bottom: B (bold),
  I (italic), U (underline), the 'Link...' button, font, size and colour.
- Adding a link works just like in Maken:
  * With text SELECTED -> that piece becomes the link (blue + underlined), the
    rest stays black.
  * Nothing selected while typing -> the URL is inserted as a clickable link at
    the cursor.
  * Nothing active -> a loose link appears that you drag into place.
  Linked text is clickable in the PDF. Select a linked piece and click 'Link...'
  with an empty URL to remove the link.
- Place text: click on the page; a text box appears where you type right away
  (multiple lines, with Enter). The box grows with your text. Apply formatting
  and links with the bar WHILE you type (the box stays open and you see
  bold/italic/underline immediately). Click elsewhere or press Esc / Ctrl+Enter
  to finish.
- Double-click a text box to edit its text again.
- Place image: choose an image, set the width, click once.
- Erase: drag a box over existing text or an image to remove it (you can still
  drag the erase box afterwards).
- Adjust a selected item with the bar (text, formatting, colour, width, link).
- 'Save as' bakes everything into a new PDF.

Sign
- Open a PDF and go to the right page.
- Type your name, choose a font, size and colour.
- Click on the page where the signature should go (you see a preview).
- 'Sign and save as' makes a signed copy.

DravePDF works fully offline on your own files.

Questions or feedback? service@dravenlock.nl
"""


class GuideDialog(QDialog):
    def __init__(self, parent, lang):
        super().__init__(parent)
        self.setWindowTitle(t("snelgids_titel", lang))
        self.resize(580, 540)
        lay = QVBoxLayout(self)
        box = QPlainTextEdit()
        box.setReadOnly(True)
        box.setPlainText(GUIDE_NL if lang == "nl" else GUIDE_EN)
        box.setObjectName("guide")
        lay.addWidget(box)
        row = QHBoxLayout()
        donate = QPushButton("\u2665 " + t("Donatie", lang))
        donate.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(DONATE_URL)))
        row.addWidget(donate)
        row.addStretch(1)
        close = QPushButton(t("Sluiten", lang))
        close.clicked.connect(self.accept)
        row.addWidget(close)
        lay.addLayout(row)


class SettingsDialog(QDialog):
    def __init__(self, parent, cfg, lang):
        super().__init__(parent)
        self.cfg = cfg
        self.setWindowTitle(t("Instellingen\u2026", lang))
        self.resize(360, 170)
        lay = QVBoxLayout(self)
        lay.addWidget(QLabel(t("Taal:", lang)))
        self.langbox = QComboBox()
        self.langbox.addItem(t("Automatisch (OS)", lang), "")
        self.langbox.addItem(t("Nederlands", lang), "nl")
        self.langbox.addItem(t("Engels", lang), "en")
        self.langbox.setCurrentIndex(
            {"": 0, "nl": 1, "en": 2}.get(cfg.get("lang", ""), 0))
        lay.addWidget(self.langbox)
        hint = QLabel("Sommige instellingen gaan pas in na herstarten."
                      if lang == "nl" else "Some settings apply after a restart.")
        hint.setObjectName("hint")
        hint.setWordWrap(True)
        lay.addWidget(hint)
        lay.addStretch(1)
        row = QHBoxLayout()
        row.addStretch(1)
        ok = QPushButton("OK")
        ok.clicked.connect(self.accept)
        row.addWidget(ok)
        lay.addLayout(row)

    def result_cfg(self):
        self.cfg["lang"] = self.langbox.currentData()
        return self.cfg


# ---------------------------------------------------------------------------
# Hoofdvenster
# ---------------------------------------------------------------------------
class DravePDF(QMainWindow):
    def __init__(self, cfg):
        super().__init__()
        self.cfg = cfg
        self.lang = _LANG
        self.setWindowTitle(APP_NAME)
        self.setWindowIcon(app_icon())
        self.resize(1040, 760)

        central = QWidget()
        self.setCentralWidget(central)
        outer = QVBoxLayout(central)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)
        outer.addWidget(self._header())

        self.tabs = QTabWidget()
        self.tabs.setObjectName("tabs")
        self.tools = ToolsTab(lambda: self.lang, self._get_dir, self._set_dir)
        self.make = MakeTab(lambda: self.lang, self._get_dir, self._set_dir)
        self.edit = EditTab(lambda: self.lang, self._get_dir, self._set_dir)
        self.sign = SignTab(lambda: self.lang, self._get_dir, self._set_dir)
        self.tools.status.connect(self._status)
        self.make.status.connect(self._status)
        self.edit.status.connect(self._status)
        self.sign.status.connect(self._status)
        self.tabs.addTab(self.tools, t("PDF-gereedschap", self.lang))
        self.tabs.addTab(self.make, t("Maken", self.lang))
        self.tabs.addTab(self.edit, t("Bewerken", self.lang))
        self.tabs.addTab(self.sign, t("Ondertekenen", self.lang))
        outer.addWidget(self.tabs, 1)

        sb = QStatusBar()
        self.setStatusBar(sb)
        sb.addPermanentWidget(QLabel("v" + APP_VERSION))
        donate = QToolButton()
        donate.setText("\u2665 " + t("Donatie", self.lang))
        donate.setObjectName("donate")
        donate.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(DONATE_URL)))
        sb.addPermanentWidget(donate)

    def _get_dir(self):
        return self.cfg.get("last_dir") or _app_dir()

    def _set_dir(self, d):
        self.cfg["last_dir"] = d
        save_config(self.cfg)

    def _status(self, msg):
        self.statusBar().showMessage(msg, 5000)

    def _header(self):
        w = QWidget()
        w.setObjectName("header")
        w.setFixedHeight(58)
        lay = QHBoxLayout(w)
        lay.setContentsMargins(14, 8, 14, 8)
        logo = QLabel()
        logo.setPixmap(logo_pixmap(34))
        lay.addWidget(logo)
        title = QLabel(APP_NAME)
        title.setObjectName("title")
        lay.addWidget(title)
        ver = QLabel("v" + APP_VERSION)
        ver.setObjectName("ver")
        lay.addWidget(ver)
        lay.addStretch(1)
        for label, slot in [(t("Instellingen\u2026", self.lang), self._settings),
                            (t("Snelgids", self.lang), self._guide),
                            (t("Over", self.lang), self._about)]:
            b = QPushButton(label)
            b.clicked.connect(lambda _=False, s=slot: s())
            lay.addWidget(b)
        return w

    def _settings(self):
        dlg = SettingsDialog(self, dict(self.cfg), self.lang)
        if dlg.exec():
            self.cfg = dlg.result_cfg()
            save_config(self.cfg)

    def _guide(self):
        GuideDialog(self, self.lang).exec()

    def _about(self):
        QMessageBox.information(
            self, t("Over", self.lang),
            "%s v%s\n\n%s\nDravenlock\n%s\n%s"
            % (APP_NAME, APP_VERSION,
               "PDF-gereedschap en ondertekenen." if self.lang == "nl"
               else "PDF tools and signing.", SUPPORT_MAIL, DONATE_URL))

    def closeEvent(self, ev):
        if self.tools.dirty:
            r = QMessageBox.question(
                self, t("Niet-opgeslagen wijzigingen", self.lang),
                t("Er zijn wijzigingen. Toch sluiten?", self.lang))
            if r != QMessageBox.StandardButton.Yes:
                ev.ignore()
                return
        ev.accept()


QSS = """
* { font-family: 'Segoe UI', sans-serif; font-size: 14px; color: %(silver)s; }
QMainWindow, QWidget { background: %(bg)s; }
#header { background: %(panel)s; border-bottom: 1px solid #23232b; }
#title { font-size: 20px; font-weight: 700; color: %(silver)s; }
#ver { color: %(mute)s; font-size: 12px; }
QTabWidget::pane { border: none; }
QTabBar::tab { background: %(panel)s; color: %(silver)s; padding: 9px 18px;
               border: 1px solid #23232b; border-bottom: none;
               border-top-left-radius: 8px; border-top-right-radius: 8px;
               font-size: 15px; }
QTabBar::tab:selected { background: %(accent)s; color: #08131f; font-weight: 700; }
QPushButton { background: %(panel)s; border: 1px solid #2c2c36; border-radius: 8px;
              padding: 7px 13px; color: %(silver)s; }
QPushButton:hover { border-color: %(accent)s; }
QPushButton:focus { border: 2px solid %(accent)s; }
QPushButton#primary { background: %(accent)s; color: #08131f; font-weight: 700;
                      border: none; }
QPushButton#primary:hover { background: #87b6e3; }
QToolButton { background: %(panel)s; border: 1px solid #2c2c36; border-radius: 8px;
              padding: 5px 9px; color: %(silver)s; min-width: 20px; }
QToolButton:hover { border-color: %(accent)s; }
QToolButton#donate { border: none; background: transparent; color: %(accent)s; }
QLineEdit, QComboBox, QSpinBox { background: %(tile)s; border: 1px solid #2c2c36;
              border-radius: 8px; padding: 7px; color: #ffffff; font-size: 15px; }
QLineEdit:focus, QComboBox:focus, QSpinBox:focus { border-color: %(accent)s; }
QComboBox QAbstractItemView { background: %(panel)s; color: %(silver)s;
              selection-background-color: %(accent)s; selection-color: #08131f; }
#muted { color: %(mute)s; font-size: 13px; }
#hint { color: %(mute)s; font-size: 12px; }
QListWidget#pages { background: #2a2a31; border: 1px solid #2c2c36;
                    border-radius: 8px; padding: 6px; }
QListWidget#pages::item { color: %(silver)s; padding: 4px; border-radius: 6px; }
QListWidget#pages::item:selected { background: %(accent)s; color: #08131f; }
QScrollArea#pageview { background: #4a4a52; border: 1px solid #2c2c36;
                       border-radius: 8px; }
QLabel#canvas { background: #4a4a52; color: %(silver)s; }
QPlainTextEdit#guide { background: %(panel)s; border: 1px solid #2c2c36;
                       border-radius: 8px; padding: 10px; font-size: 14px; }
QPlainTextEdit#bigtext { background: %(tile)s; border: 1px solid #2c2c36;
                         border-radius: 8px; padding: 10px; color: #ffffff;
                         font-size: 15px; }
QTextEdit#paper { background: #ffffff; color: #111111; border: 1px solid #2c2c36;
                  border-radius: 8px; padding: 14px; font-size: 15px; }
QToolButton#fmtbold { font-weight: 800; min-width: 26px; }
QToolButton#fmtital { font-style: italic; min-width: 26px; }
QToolButton#fmtund { text-decoration: underline; min-width: 26px; }
QToolButton#fmtbold:checked, QToolButton#fmtital:checked,
QToolButton#fmtund:checked { background: %(accent)s; color: #08131f; }
QFrame#rubber { background: rgba(224,162,58,45); border: 1px dashed %(warn)s; }
QLineEdit#inline, QPlainTextEdit#inline {
    background: #fff7df; color: #10131a; border: 2px solid %(accent)s;
    border-radius: 3px; padding: 1px 3px; }
QDialog { background: %(bg)s; }
QStatusBar { background: %(panel)s; }
""" % {"bg": BG, "panel": PANEL, "tile": TILE, "silver": SILVER,
       "mute": MUTE, "accent": ACCENT, "warn": WARN}


def _install_excepthook():
    import traceback

    def hook(exctype, value, tb):
        msg = "".join(traceback.format_exception(exctype, value, tb))
        try:
            with open(os.path.join(_app_dir(), "dravepdf-fout.txt"),
                      "w", encoding="utf-8") as f:
                f.write(msg)
        except Exception:
            pass
        try:
            if QApplication.instance():
                QMessageBox.critical(None, "DravePDF - fout",
                                     "Er ging iets mis:\n\n" + msg[-1500:]
                                     + "\n\n(Ook opgeslagen in dravepdf-fout.txt)")
        except Exception:
            pass
        sys.__excepthook__(exctype, value, tb)

    sys.excepthook = hook


def main():
    global _LANG
    _install_excepthook()
    app = QApplication(sys.argv)
    try:
        cfg = load_config()
        _LANG = detect_lang(cfg)
        app.setStyleSheet(QSS)
        win = DravePDF(cfg)
        win.show()
    except Exception:
        sys.excepthook(*sys.exc_info())
        return
    try:  # Dravenlock: stille update-check (uit te zetten; Ctrl+Shift+U = met de hand)
        import drave_update
        drave_update.start(win, 'DravePDF', APP_VERSION)
    except Exception:
        pass
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
