"""Build printable HTML from the campaign markdown."""

import argparse
import html
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import markdown

type Kind = Literal["karta", "sekcja", "kartka", "mapa"]

MARKDOWN_EXTENSIONS = ["tables", "fenced_code", "sane_lists"]
LINK_PATTERN = re.compile(r"(?<!!)\[([^\]]+)\]\(([^)\s]+)\)")
FENCE_PATTERN = re.compile(r"(^```.*?^```)", re.M | re.S)
HEADING_PATTERN = re.compile(r"<h([1-6])>(.*?)</h\1>", re.S)
HREF_PATTERN = re.compile(r'<a href="([^"]*)"')
ID_PATTERN = re.compile(r'\sid="([^"]*)"')
TAG_PATTERN = re.compile(r"<[^>]+>")

STYLESHEET = """
@page {
  size: A4;
  margin: 11mm 11mm 13mm 11mm;
  @bottom-right {
    content: counter(page);
    font-family: "Segoe UI", Calibri, sans-serif;
    font-size: 8pt;
    color: #666;
  }
}
* { box-sizing: border-box; }
html { font-family: "Segoe UI", Calibri, sans-serif; color: #241c16; }
body {
  font-size: 10.5pt;
  line-height: 1.38;
  margin: 0 auto;
  max-width: 190mm;
  background: #fffdf8;
}
h1 { font-size: 16.5pt; line-height: 1.2; margin: 0 0 0.35em; break-after: avoid; }
h2 {
  font-size: 13pt;
  line-height: 1.25;
  margin: 0.9em 0 0.3em;
  break-after: avoid;
  border-bottom: 0.4pt solid #e4d3b5;
}
h3 { font-size: 11.5pt; margin: 0.8em 0 0.25em; break-after: avoid; }
h4 { font-size: 10.5pt; margin: 0.7em 0 0.2em; break-after: avoid; }
p { margin: 0.35em 0; }
ul, ol { margin: 0.3em 0 0.5em; padding-left: 1.2em; }
li { margin: 0.12em 0; }
a { color: #6b3a1f; }
strong { font-weight: 650; }
hr { border: none; border-top: 0.4pt solid #e4d3b5; margin: 0.7em 0; }
table {
  width: 100%;
  border-collapse: collapse;
  margin: 0.4em 0 0.7em;
  font-size: 9pt;
  line-height: 1.3;
}
th, td {
  border: 0.4pt solid #d9cbb3;
  padding: 2px 5px;
  vertical-align: top;
  text-align: left;
}
th { background: #f4efe4; font-weight: 650; }
thead { display: table-header-group; }
tr { break-inside: avoid; }
blockquote {
  margin: 0.45em 0;
  padding: 0.35em 0.7em;
  border-left: 2.5pt solid #b8893a;
  background: #faf6ee;
}
pre {
  white-space: pre-wrap;
  font-family: Consolas, "Cascadia Mono", monospace;
  font-size: 8pt;
  line-height: 1.25;
  background: #f7f4ee;
  border: 0.4pt solid #e4d3b5;
  padding: 0.45em 0.55em;
  break-inside: avoid;
}
code { font-family: Consolas, "Cascadia Mono", monospace; font-size: 0.92em; }
.meta {
  font-family: Consolas, "Cascadia Mono", monospace;
  font-size: 8pt;
  line-height: 1.3;
  color: #5c5348;
  background: #f7f4ee;
  border: 0.4pt solid #e4d3b5;
  padding: 0.4em 0.55em;
  white-space: pre-wrap;
}
.pieczatka {
  display: inline-block;
  margin: 0 0 0.55em;
  padding: 0.12em 0.45em;
  border: 1.4pt solid #8c2f2f;
  color: #8c2f2f;
  font-size: 9pt;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}
.spis { margin: 0 0 0.8em; }
.spis p { margin: 0 0 0.15em; font-weight: 650; }
.spis ol { margin: 0; }
.uwaga { color: #8c2f2f; font-weight: 650; }
.sekcja.nowa, .kartka { break-before: page; }
.karta { font-size: 8.6pt; line-height: 1.16; }
.karta h1 { font-size: 14pt; margin-bottom: 0.08em; }
.karta h2 {
  font-size: 10pt;
  margin: 0.28em 0 0.06em;
  border: none;
  color: #6b3a1f;
}
.karta p { margin: 0.08em 0; }
.karta table { font-size: 7.7pt; margin: 0.1em 0 0.16em; }
.karta th, .karta td { padding: 0 3px; }
.mapa pre, .mapa pre code {
  white-space: pre;
  font-size: 7.5pt;
  line-height: 1.15;
  background: transparent;
  border: none;
  padding: 0;
}
.kartka {
  border: 0.8pt solid #c4a574;
  padding: 8mm 9mm;
}
.arkusz .kartka { break-before: auto; break-inside: avoid; }
.ciecie {
  margin: 5mm 0 6mm;
  border-top: 0.8pt dashed #444;
  text-align: center;
  color: #555;
  font-size: 8pt;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}
.ciecie span {
  display: inline-block;
  position: relative;
  top: -0.7em;
  padding: 0 0.6em;
  background: #fffdf8;
}
th, .pieczatka, blockquote, pre, .meta {
  -webkit-print-color-adjust: exact;
  print-color-adjust: exact;
}
@media screen {
  html { background: #e4ddd2; }
  body { margin: 8mm auto; padding: 8mm; box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08); }
}
@media print {
  html, body { background: white; max-width: none; margin: 0; padding: 0; box-shadow: none; }
  a { color: inherit; text-decoration: none; }
  .powrot, .spis-ekran { display: none !important; }
  .kartka { border-color: #bbb; }
  .ciecie span { background: white; }
}
"""


@dataclass(frozen=True)
class Piece:
    source: Path
    anchor: str
    kind: Kind


@dataclass(frozen=True)
class Book:
    output: Path
    title: str
    pieces: tuple[Piece, ...]
    contents_on_paper: bool
    for_players: bool


@dataclass(frozen=True)
class Target:
    output: Path
    anchor: str


@dataclass(frozen=True)
class Handout:
    slug: str
    title: str
    markdown: str


def build_parser() -> argparse.ArgumentParser:
    """Return the command line parser.

    :return: parser for the campaign root
    """
    parser = argparse.ArgumentParser(description="Build printable HTML from the campaign markdown.")
    parser.add_argument("--root", type=existing_directory, default=None)
    return parser


def existing_directory(value: str) -> Path:
    """Reject a path that is not a directory.

    :param value: path given on the command line
    :return: absolute directory
    :raises argparse.ArgumentTypeError: when the path is not a directory
    """
    path = Path(value)
    if not path.is_dir():
        raise argparse.ArgumentTypeError(f"{value} is not a directory")
    return path.resolve()


def main(argv: list[str] | None = None) -> int:
    """Write the printable HTML files.

    :param argv: command arguments without the program name
    :return: process exit code
    """
    try:
        return build_pages(argv)
    except KeyboardInterrupt:
        return 0


def build_pages(argv: list[str] | None) -> int:
    """Render every book and write it next to this script.

    :param argv: command arguments without the program name
    :return: process exit code
    """
    arguments = build_parser().parse_args(argv)
    root = default_root() if arguments.root is None else arguments.root
    books = collect_books(root)
    if books is None:
        return 1
    handouts = read_handouts(root)
    if handouts is None:
        return 1
    catalog = catalog_of(books)
    if catalog is None:
        return 1
    handout_index = root / "druk" / "mg" / "rekwizyty" / "index.html"
    source = (root / "gracze" / "rekwizyty.md").resolve()
    if source in catalog:
        print(f"buduj.py failed: {source} is listed twice", file=sys.stderr)
        return 1
    catalog[source] = Target(handout_index, "spis")
    pages = render_books(books, catalog)
    if pages is None:
        return 1
    pages.update(render_handouts(root, handouts))
    pages.update(render_indexes(root, books, handouts))
    problems = missing_targets(pages)
    if problems:
        print("buduj.py failed: broken links", file=sys.stderr)
        for problem in problems:
            print(problem, file=sys.stderr)
        return 1
    for path, page in pages.items():
        if not write_page(path, page):
            return 1
    print(f"Wrote {len(pages)} files.")
    return 0


def default_root() -> Path:
    """Return the campaign directory that contains this script.

    :return: repository root
    """
    return Path(__file__).resolve().parents[1]


def collect_books(root: Path) -> list[Book] | None:
    """List the player packets and the grouped game master books.

    :param root: campaign directory
    :return: books to render, or None when a source file is missing
    """
    players = character_books(root)
    if players is None:
        return None
    master = master_books(root)
    if master is None:
        return None
    return players + master


def character_books(root: Path) -> list[Book] | None:
    """Build one book per character, starting with the print card.

    :param root: campaign directory
    :return: player books, or None when a source file is missing
    """
    names = (
        ("pip-iskra-torren", "Pip „Iskra” Torren"),
        ("luma-bramblewick", "Luma Bramblewick"),
        ("zizzle-stormpocket", "Zizzle Stormpocket"),
        ("orrin-quill", "Orrin Quill"),
        ("nixa-embercoil", "Nixa Embercoil"),
    )
    books: list[Book] = []
    for slug, title in names:
        pieces = character_pieces(root, slug)
        if pieces is None:
            return None
        output = root / "druk" / "postacie" / f"{slug}.html"
        books.append(Book(output, title, tuple(pieces), False, True))
    player_map = root / "gracze" / "mapa.md"
    if not player_map.is_file():
        print(f"buduj.py failed: missing {player_map}", file=sys.stderr)
        return None
    books.append(
        Book(
            root / "druk" / "postacie" / "mapa.html",
            "Mapa dla graczy",
            (Piece(player_map, "mapa", "mapa"),),
            False,
            True,
        )
    )
    return books


def character_pieces(root: Path, slug: str) -> list[Piece] | None:
    """Order the card, the history, the full sheet, and the papers in a pocket.

    :param root: campaign directory
    :param slug: character folder name
    :return: pieces in print order, or None when a required file is missing
    """
    folder = root / "gracze" / "postacie" / slug
    card = root / "gracze" / "karty-do-druku" / f"{slug}.md"
    core: tuple[tuple[Path, str, Kind], ...] = (
        (card, "karta", "karta"),
        (folder / "backstory.md", "historia", "sekcja"),
        (folder / "sheet.md", "karta-pelna", "sekcja"),
        (folder / "spells.md", "czary", "sekcja"),
        (folder / "feats.md", "atuty", "sekcja"),
        (folder / "features.md", "zdolnosci", "sekcja"),
        (folder / "state.md", "stan", "sekcja"),
    )
    pieces: list[Piece] = []
    known: set[str] = set()
    for path, anchor, kind in core:
        if not path.is_file():
            print(f"buduj.py failed: missing {path}", file=sys.stderr)
            return None
        pieces.append(Piece(path, anchor, kind))
        known.add(path.name)
    extras = sorted(path for path in folder.glob("*.md") if path.name not in known)
    for path in extras:
        pieces.append(Piece(path, path.stem, "kartka"))
    return pieces


def master_books(root: Path) -> list[Book] | None:
    """Group the game master files into a handful of printable books.

    :param root: campaign directory
    :return: game master books, or None when a source file is missing
    """
    master = root / "MG"
    meetings = (
        "S01-atrium-alarm.md",
        "S02-studenci-brody.md",
        "S03-biblioteka-schemat.md",
        "S04-splot-kanapka.md",
        "S05-magazyn-farba.md",
        "S06-tablica-triady.md",
        "S07-kapitan-klik.md",
        "S08-ozywione-narzedzia.md",
        "S09-zywiolak-stazysta.md",
        "S10-szept-brina.md",
        "S11-list-smoka.md",
        "S12-zasadzka-brod.md",
    )
    groups: tuple[tuple[str, str, tuple[tuple[Path, str], ...]], ...] = (
        (
            "sesja.html",
            "Przy stole",
            (
                (master / "README.md", "wstep"),
                (master / "plan-sesji.md", "plan-sesji"),
                (master / "rekwizyty-kiedy.md", "rekwizyty-kiedy"),
            ),
        ),
        (
            "mapa.html",
            "Mapa MG",
            ((master / "mapa.md", "mapa"),),
        ),
        (
            "spotkania.html",
            "Spotkania",
            ((master / "spotkania" / "README.md", "spis"),)
            + tuple((master / "spotkania" / name, Path(name).stem) for name in meetings),
        ),
        (
            "zagadki.html",
            "Zagadki i kartki",
            (
                (master / "zagadki.md", "zagadki"),
                (master / "ekwipunek-z-historii.md", "ekwipunek-z-historii"),
            ),
        ),
        (
            "swiat.html",
            "Bohaterowie i akademia",
            (
                (master / "bn.md", "bn"),
                (master / "opisy" / "lokacje.md", "lokacje"),
                (master / "opisy" / "historia-posagu.md", "historia-posagu"),
                (master / "opisy" / "smok-i-koboldy.md", "smok-i-koboldy"),
            ),
        ),
        (
            "prompty.html",
            "Prompty",
            (
                (master / "prompty" / "README.md", "spis"),
                (master / "prompty" / "postacie.md", "postacie"),
                (master / "prompty" / "sceny.md", "sceny"),
                (master / "prompty" / "przedstawienie.md", "przedstawienie"),
            ),
        ),
    )
    books: list[Book] = []
    for filename, title, parts in groups:
        pieces: list[Piece] = []
        for path, anchor in parts:
            if not path.is_file():
                print(f"buduj.py failed: missing {path}", file=sys.stderr)
                return None
            kind: Kind = "mapa" if filename == "mapa.html" else "sekcja"
            pieces.append(Piece(path, anchor, kind))
        output = root / "druk" / "mg" / filename
        show_contents = filename != "mapa.html"
        books.append(Book(output, title, tuple(pieces), show_contents, False))
    return books


def catalog_of(books: list[Book]) -> dict[Path, Target] | None:
    """Map each source file to the printed page that contains it.

    :param books: books about to be rendered
    :return: catalog, or None when the same file is listed twice
    """
    catalog: dict[Path, Target] = {}
    for book in books:
        for piece in book.pieces:
            source = piece.source.resolve()
            if source in catalog:
                print(f"buduj.py failed: {source} is listed twice", file=sys.stderr)
                return None
            catalog[source] = Target(book.output, piece.anchor)
    return catalog


def render_books(books: list[Book], catalog: dict[Path, Target]) -> dict[Path, str] | None:
    """Render the books to HTML pages held in memory.

    :param books: player and game master books
    :param catalog: source path to printed target
    :return: pages by output path, or None when a file cannot be read
    """
    pages: dict[Path, str] = {}
    for book in books:
        page = render_book(book, catalog)
        if page is None:
            return None
        pages[book.output] = page
    return pages


def render_book(book: Book, catalog: dict[Path, Target]) -> str | None:
    """Render one printable document.

    :param book: document definition
    :param catalog: source path to printed target
    :return: full HTML page, or None when a piece cannot be read
    """
    articles: list[str] = []
    contents: list[tuple[str, str]] = []
    for index, piece in enumerate(book.pieces):
        rendered = render_piece(piece, book, catalog, index > 0)
        if rendered is None:
            return None
        article, heading = rendered
        articles.append(article)
        contents.append((piece.anchor, heading or piece.anchor))
    body = "".join(
        (
            back_link(book),
            stamp(book),
            contents_block(contents, book.contents_on_paper),
            "".join(articles),
        )
    )
    return page_html(book.title, body)


def render_piece(
    piece: Piece,
    book: Book,
    catalog: dict[Path, Target],
    is_later: bool,
) -> tuple[str, str] | None:
    """Convert one markdown file into a section.

    :param piece: source file and its anchor
    :param book: document that will contain the section
    :param catalog: source path to printed target
    :param is_later: whether a page break should precede this section
    :return: article HTML and its title, or None when the file cannot be read
    """
    text = read_text(piece.source)
    if text is None:
        return None
    front, body = split_front_matter(text)
    rewritten = rewrite_links(body, piece.source, book, catalog)
    converted = markdown.markdown(rewritten, extensions=MARKDOWN_EXTENSIONS)
    stamped = stamp_headings(converted, piece.anchor)
    inner = insert_meta(stamped, render_meta(front))
    css = section_class(piece.kind, is_later)
    article = f'<article class="{css}">{inner}</article>'
    return article, first_heading(stamped)


def read_text(path: Path) -> str | None:
    """Read a markdown file as UTF 8.

    :param path: file to read
    :return: file text, or None when the read fails
    """
    try:
        return path.read_text(encoding="utf-8").replace("\r\n", "\n")
    except (OSError, UnicodeError) as error:
        print(f"buduj.py failed: {error}", file=sys.stderr)
        return None


def split_front_matter(text: str) -> tuple[str, str]:
    """Separate a leading metadata block from the markdown body.

    :param text: full file text
    :return: metadata block and the remaining markdown
    """
    if not text.startswith("---\n"):
        return "", text
    end = text.find("\n---\n", 4)
    if end == -1:
        return "", text
    return text[4:end], text[end + 5 :]


def rewrite_links(text: str, source: Path, book: Book, catalog: dict[Path, Target]) -> str:
    """Point markdown links at headings inside the printed books.

    :param text: markdown outside of any metadata block
    :param source: file the links were written in
    :param book: document being rendered
    :param catalog: source path to printed target
    :return: markdown with rewritten links
    """
    parts = FENCE_PATTERN.split(text)
    rewritten: list[str] = []
    for index, part in enumerate(parts):
        if index % 2 == 1:
            rewritten.append(part)
            continue
        rewritten.append(
            LINK_PATTERN.sub(
                lambda match: replace_link(match, source, book, catalog),
                part,
            )
        )
    return "".join(rewritten)


def replace_link(
    match: re.Match[str],
    source: Path,
    book: Book,
    catalog: dict[Path, Target],
) -> str:
    """Rewrite one markdown link, or keep its label when it has no printed target.

    :param match: link label and destination
    :param source: file that contains the link
    :param book: document being rendered
    :param catalog: source path to printed target
    :return: replacement markdown
    """
    label = match.group(1)
    href = match.group(2)
    if "://" in href or href.startswith("mailto:"):
        return match.group(0)
    path_text, separator, fragment = href.partition("#")
    if path_text == "":
        current = catalog[source.resolve()]
        ident = current.anchor if fragment == "" else f"{current.anchor}-{fragment}"
        return f"[{label}](#{ident})"
    target = catalog.get((source.parent / path_text).resolve())
    if target is None or not target_allowed(book, target):
        return label
    ident = target.anchor if fragment == "" else f"{target.anchor}-{fragment}"
    if target.output.resolve() == book.output.resolve():
        return f"[{label}](#{ident})"
    relative = Path(os.path.relpath(target.output, book.output.parent)).as_posix()
    return f"[{label}]({relative}#{ident})"


def target_allowed(book: Book, target: Target) -> bool:
    """Keep game master pages out of the files handed to players.

    :param book: document being rendered
    :param target: printed page a link would open
    :return: whether the link may stay
    """
    if book.for_players and target.output.parent.name != "postacie":
        return False
    return True


def stamp_headings(html_text: str, anchor: str) -> str:
    """Give each heading a stable id that matches the markdown anchors.

    :param html_text: HTML produced from one markdown file
    :param anchor: id of this file inside the printed book
    :return: HTML with heading ids
    """
    seen: dict[str, int] = {}

    def replace(match: re.Match[str]) -> str:
        level = match.group(1)
        inner = match.group(2)
        if level == "1" and anchor not in seen:
            ident = anchor
        else:
            slug = slugify(strip_tags(inner))
            ident = f"{anchor}-{slug}" if slug else f"{anchor}-sekcja"
        count = seen.get(ident, 0)
        seen[ident] = count + 1
        if count:
            ident = f"{ident}-{count}"
        safe = html.escape(ident, quote=True)
        return f'<h{level} id="{safe}">{inner}</h{level}>'

    return HEADING_PATTERN.sub(replace, html_text)


def slugify(text: str) -> str:
    """Turn heading text into the anchor used by the markdown links.

    :param text: visible heading text
    :return: anchor fragment without the file prefix
    """
    plain = re.sub(r"[*_`]", "", text).strip().lower()
    plain = re.sub(r"[^\w\s-]", "", plain, flags=re.UNICODE)
    return re.sub(r"\s", "-", plain)


def strip_tags(html_text: str) -> str:
    """Remove tags and decode entities.

    :param html_text: HTML fragment
    :return: plain text
    """
    return html.unescape(TAG_PATTERN.sub("", html_text))


def insert_meta(html_text: str, meta_html: str) -> str:
    """Place the metadata block under the title.

    :param html_text: section HTML
    :param meta_html: rendered metadata, empty when the file has none
    :return: section HTML
    """
    if meta_html == "":
        return html_text
    match = re.search(r"</h1>", html_text)
    if match is None:
        return meta_html + html_text
    end = match.end()
    return html_text[:end] + meta_html + html_text[end:]


def render_meta(front: str) -> str:
    """Render a metadata block as a small preformatted note.

    :param front: text between the opening fences, without the fences
    :return: HTML, empty when there is no metadata
    """
    if front.strip() == "":
        return ""
    return f'<pre class="meta">{html.escape(front.strip())}</pre>'


def section_class(kind: Kind, is_later: bool) -> str:
    """Choose the CSS class, including a page break before later sections.

    :param kind: card, section, or pocket note
    :param is_later: whether this is not the first piece of the book
    :return: class attribute value
    """
    if is_later and kind == "sekcja":
        return "sekcja nowa"
    return kind


def first_heading(html_text: str) -> str:
    """Return the text of the first h1.

    :param html_text: section HTML
    :return: heading text, or an empty string when there is no h1
    """
    match = re.search(r"<h1[^>]*>(.*?)</h1>", html_text, flags=re.S)
    if match is None:
        return ""
    return strip_tags(match.group(1)).strip()


def back_link(book: Book) -> str:
    """Return a screen only link to the folder index.

    :param book: document being rendered
    :return: HTML paragraph
    """
    label = "Wszystkie postacie" if book.for_players else "Spis materiałów MG"
    return f'<p class="powrot"><a href="index.html">{label}</a></p>'


def stamp(book: Book) -> str:
    """Return the game master banner.

    :param book: document being rendered
    :return: HTML, empty for a player packet
    """
    if book.for_players:
        return ""
    return '<p class="pieczatka">Tylko dla Mistrza Gry</p>'


def contents_block(items: list[tuple[str, str]], on_paper: bool) -> str:
    """Render the list of sections.

    :param items: anchor and visible title
    :param on_paper: whether the list is included in the printout
    :return: navigation HTML
    """
    css = "spis" if on_paper else "spis spis-ekran"
    rows = "\n".join(
        f'<li><a href="#{html.escape(anchor, quote=True)}">{html.escape(label)}</a></li>'
        for anchor, label in items
    )
    return f'<nav class="{css}"><p>Spis</p><ol>{rows}</ol></nav>'


def page_html(title: str, body: str) -> str:
    """Wrap a body in a complete printable page.

    :param title: document title
    :param body: inner HTML
    :return: HTML document
    """
    safe_title = html.escape(title)
    return (
        "<!DOCTYPE html>\n"
        '<html lang="pl">\n'
        "<head>\n"
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f"<title>{safe_title}</title>\n"
        f"<style>{STYLESHEET}</style>\n"
        "</head>\n"
        "<body>\n"
        f"{body}\n"
        "</body>\n"
        "</html>\n"
    )


def read_handouts(root: Path) -> list[Handout] | None:
    """Split the prop sheet and append the papers from pockets.

    :param root: campaign directory
    :return: handouts in order, or None when the sheet is missing or incomplete
    """
    path = root / "gracze" / "rekwizyty.md"
    if not path.is_file():
        print(f"buduj.py failed: missing {path}", file=sys.stderr)
        return None
    try:
        text = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    except (OSError, UnicodeError) as error:
        print(f"buduj.py failed: {error}", file=sys.stderr)
        return None
    matches = list(re.finditer(r"^## (R\d+) — (.+)$", text, flags=re.M))
    if len(matches) != 9:
        print("buduj.py failed: expected nine handouts", file=sys.stderr)
        return None
    handouts: list[Handout] = []
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        kept = [line for line in text[start:end].splitlines() if line.strip() != "---"]
        body = "\n".join(kept).strip()
        title = f"{match.group(1)} — {match.group(2)}"
        handouts.append(Handout(match.group(1).lower(), title, f"# {title}\n\n{body}\n"))
    carried = carried_papers(root)
    if carried is None:
        return None
    handouts.extend(carried)
    return handouts


def carried_papers(root: Path) -> list[Handout] | None:
    """Read the letters and the barrier copy the characters already carry.

    :param root: campaign directory
    :return: papers in print order, or None when a file is missing
    """
    relative_paths = (
        "gracze/postacie/orrin-quill/schemat-bariery.md",
        "gracze/postacie/nixa-embercoil/list-od-kuzyna.md",
        "gracze/postacie/zizzle-stormpocket/list-legalny-gnom.md",
    )
    papers: list[Handout] = []
    for relative in relative_paths:
        path = root / relative
        if not path.is_file():
            print(f"buduj.py failed: missing {path}", file=sys.stderr)
            return None
        try:
            text = path.read_text(encoding="utf-8").replace("\r\n", "\n")
        except (OSError, UnicodeError) as error:
            print(f"buduj.py failed: {error}", file=sys.stderr)
            return None
        title = path.stem
        for line in text.splitlines():
            if line.startswith("# "):
                title = line[2:].strip()
                break
        if not text.endswith("\n"):
            text += "\n"
        papers.append(Handout(path.stem, title, text))
    return papers


def render_handouts(root: Path, handouts: list[Handout]) -> dict[Path, str]:
    """Write each handout, one cut sheet, and their index.

    :param root: campaign directory
    :param handouts: props in handout order
    :return: pages by output path
    """
    folder = root / "druk" / "mg" / "rekwizyty"
    pages: dict[Path, str] = {}
    for handout in handouts:
        body = (
            '<p class="powrot"><a href="index.html">Wszystkie rekwizyty</a></p>'
            '<article class="kartka">'
            + markdown.markdown(handout.markdown, extensions=MARKDOWN_EXTENSIONS)
            + "</article>"
        )
        pages[folder / f"{handout.slug}.html"] = page_html(handout.title, body)
    stacked: list[str] = []
    for index, handout in enumerate(handouts):
        if index:
            stacked.append('<p class="ciecie"><span>tnij</span></p>')
        stacked.append(
            '<article class="kartka">'
            + markdown.markdown(handout.markdown, extensions=MARKDOWN_EXTENSIONS)
            + "</article>"
        )
    stacked_body = (
        '<p class="powrot"><a href="index.html">Wszystkie rekwizyty</a></p>'
        '<div class="arkusz">'
        + "".join(stacked)
        + "</div>"
    )
    pages[folder / "wszystkie.html"] = page_html("Wszystkie rekwizyty", stacked_body)
    items = "\n".join(
        [
            link_item(
                "wszystkie.html",
                "Wszystkie na jednej kartce",
                "Rekwizyty, listy i schemat, z linią „tnij”.",
            )
        ]
        + [
            link_item(f"{handout.slug}.html", handout.title, "Osobna kartka do wycięcia.")
            for handout in handouts
        ]
    )
    index_body = (
        '<p class="pieczatka">Tylko dla Mistrza Gry</p>'
        '<p class="powrot"><a href="../index.html">Spis materiałów MG</a></p>'
        '<h1 id="spis">Rekwizyty</h1>'
        "<p>Możesz wydrukować każdą kartkę osobno albo wszystkie naraz i pociąć wzdłuż linii.</p>"
        f"<ul>{items}</ul>"
    )
    pages[folder / "index.html"] = page_html("Rekwizyty", index_body)
    return pages


def render_indexes(root: Path, books: list[Book], handouts: list[Handout]) -> dict[Path, str]:
    """Build the three opening pages.

    :param root: campaign directory
    :param books: rendered books, used for the lists
    :return: index pages by output path
    """
    druk = root / "druk"
    player_books = [book for book in books if book.for_players]
    master = [book for book in books if not book.for_players]
    player_detail = (
        "Karta na pierwszą stronę, potem historia, pełna karta, czary, atuty, "
        "zdolności, stan i kartki z kieszeni."
    )
    master_blurbs = {
        "sesja.html": "Plan sesji, zegar powodzi, kiedy wręczać rekwizyty i mapa.",
        "spotkania.html": "Spis i spotkania od S01 do S12.",
        "zagadki.html": "Rozwiązania napraw i klucz do kartek, które postacie noszą od startu.",
        "swiat.html": "Bohaterowie niezależni, lokacje, historia posągu, smok i jego ekipa.",
        "prompty.html": "Polecenia do grafik i do tekstowego przedstawienia drużyny.",
    }
    master_blurbs["mapa.html"] = "Mapa z oznaczeniami napraw, zegara i atrium."
    master_blurbs["sesja.html"] = "Plan sesji, zegar powodzi i kiedy wręczać rekwizyty."
    player_items = "\n".join(
        link_item(book.output.name, book.title, book_detail(book, player_detail))
        for book in player_books
    )
    master_items = "\n".join(
        link_item(book.output.name, book.title, master_blurbs[book.output.name]) for book in master
    )
    every_player = "\n".join(
        link_item(
            f"postacie/{book.output.name}",
            book.title,
            book_detail(book, player_detail),
        )
        for book in player_books
    )
    every_master = "\n".join(
        link_item(f"mg/{book.output.name}", book.title, master_blurbs[book.output.name])
        for book in master
    )
    slips_here = "\n".join(
        [
            link_item(
                "rekwizyty/wszystkie.html",
                "Wszystkie na jednej kartce",
                "Rekwizyty, listy i schemat, z linią „tnij”.",
            )
        ]
        + [
            link_item(f"rekwizyty/{handout.slug}.html", handout.title, "Osobna kartka.")
            for handout in handouts
        ]
    )
    slips_root = "\n".join(
        [
            link_item(
                "mg/rekwizyty/wszystkie.html",
                "Wszystkie na jednej kartce",
                "Rekwizyty, listy i schemat, z linią „tnij”.",
            )
        ]
        + [
            link_item(f"mg/rekwizyty/{handout.slug}.html", handout.title, "Osobna kartka.")
            for handout in handouts
        ]
    )
    player_body = (
        "<h1>Karty postaci</h1>"
        "<p>Każda postać jest w jednym pliku, a mapa skrzydła osobno. "
        "Drukuj na A4, w skali 100%, bez nagłówków i stopek przeglądarki. "
        "Pola ☐ odhaczaj ołówkiem.</p>"
        f"<ul>{player_items}</ul>"
    )
    master_body = (
        '<p class="pieczatka">Tylko dla Mistrza Gry</p>'
        "<h1>Materiały Mistrza Gry</h1>"
        "<p>Plan, osobna mapa i pozostałe materiały. Drukuj na A4, w skali 100%.</p>"
        f"<ul>{master_items}</ul>"
        "<h2>Rekwizyty</h2>"
        "<ul>"
        + link_item("rekwizyty/index.html", "Spis rekwizytów", "Rekwizyty, listy i schemat.")
        + "\n"
        + slips_here
        + "</ul>"
    )
    root_body = (
        "<h1>Wydruki</h1>"
        "<p>Wszystkie pliki HTML. Drukuj na A4, w skali 100%, "
        "bez nagłówków i stopek przeglądarki.</p>"
        '<p class="uwaga">Pliki Mistrza Gry zawierają tajemnice. '
        "Graczom dawaj tylko pliki postaci.</p>"
        '<p><a href="/katalog">Cała struktura plików</a><br>'
        "Markdown i katalogi kampanii. Działa przy uruchomionym serwerze.</p>"
        "<h2>Postacie</h2>"
        "<ul>"
        + link_item("postacie/index.html", "Spis postaci", "Sam spis, bez treści kart.")
        + "\n"
        + every_player
        + "</ul>"
        "<h2>Mistrz Gry</h2>"
        "<ul>"
        + link_item("mg/index.html", "Spis materiałów MG", "Sam spis, bez treści sesji.")
        + "\n"
        + every_master
        + "</ul>"
        "<h2>Rekwizyty</h2>"
        "<ul>"
        + link_item("mg/rekwizyty/index.html", "Spis rekwizytów", "Rekwizyty, listy i schemat.")
        + "\n"
        + slips_root
        + "</ul>"
    )
    return {
        druk / "postacie" / "index.html": page_html("Karty postaci", player_body),
        druk / "mg" / "index.html": page_html("Materiały Mistrza Gry", master_body),
        druk / "index.html": page_html("Wydruki", root_body),
    }


def book_detail(book: Book, character_detail: str) -> str:
    """Describe one player file on the index.

    :param book: player book
    :param character_detail: text used for a character packet
    :return: short description
    """
    if book.output.name == "mapa.html":
        return "Mapa skrzydła bez tajemnic."
    return character_detail


def link_item(href: str, title: str, detail: str) -> str:
    """Render one entry on an index page.

    :param href: relative link
    :param title: visible name
    :param detail: short description under the name
    :return: list item HTML
    """
    return (
        f'<li><a href="{href}">{html.escape(title)}</a>'
        f"<br>{html.escape(detail)}</li>"
    )


def missing_targets(pages: dict[Path, str]) -> list[str]:
    """Find links that do not land on a heading in these pages.

    :param pages: rendered HTML by output path
    :return: problem descriptions
    """
    ids_by_file = {path.resolve(): set(ID_PATTERN.findall(page)) for path, page in pages.items()}
    problems: list[str] = []
    for path, page in pages.items():
        for href in HREF_PATTERN.findall(page):
            problems.extend(problems_for_href(path, href, ids_by_file))
        problems.extend(duplicate_ids(path, page))
    return problems


def problems_for_href(path: Path, href: str, ids_by_file: dict[Path, set[str]]) -> list[str]:
    """Check one href against the rendered pages.

    :param path: page that contains the link
    :param href: link destination
    :param ids_by_file: heading ids present in each page
    :return: problem descriptions
    """
    if href.startswith(("http://", "https://", "mailto:", "/")):
        return []
    file_part, separator, ident = href.partition("#")
    if file_part == "":
        target = path.resolve()
    else:
        target = (path.parent / file_part).resolve()
    if target not in ids_by_file:
        return [f"{path.name}: missing file {href}"]
    if separator and ident not in ids_by_file[target]:
        return [f"{path.name}: missing {href}"]
    return []


def duplicate_ids(path: Path, page: str) -> list[str]:
    """Report repeated id attributes.

    :param path: page being checked
    :param page: HTML text
    :return: problem descriptions
    """
    seen: set[str] = set()
    problems: list[str] = []
    for ident in ID_PATTERN.findall(page):
        if ident in seen:
            problems.append(f"{path.name}: duplicate id {ident}")
        seen.add(ident)
    return problems


def write_page(path: Path, page: str) -> bool:
    """Write one HTML file, creating the parent folder when needed.

    :param path: destination
    :param page: full HTML document
    :return: False when the write fails
    """
    if not path.parent.is_dir():
        path.parent.mkdir(parents=True, exist_ok=True)
    try:
        path.write_text(page, encoding="utf-8", newline="\n")
    except OSError as error:
        print(f"buduj.py failed: {error}", file=sys.stderr)
        return False
    return True


if __name__ == "__main__":
    raise SystemExit(main())
