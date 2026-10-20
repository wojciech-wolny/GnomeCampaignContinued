"""Serve the campaign files and the print index."""

import argparse
import html
import io
import sys
import urllib.parse
from functools import partial
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HOST = "127.0.0.1"
DEFAULT_PORT = 8080
CAMPAIGN_ROOT = Path(__file__).resolve().parents[1]
HIDDEN_NAMES = {".git", ".idea", ".venv", "__pycache__"}


class ReuseServer(ThreadingHTTPServer):
    """Allow the port to be opened again right after a restart."""

    allow_reuse_address = True


class CampaignHandler(SimpleHTTPRequestHandler):
    """Serve the start page, the file tree, and markdown ready to read."""

    extensions_map = {
        **SimpleHTTPRequestHandler.extensions_map,
        ".md": "text/plain; charset=utf-8",
    }

    def send_head(self) -> io.IOBase | None:
        """Serve the start page, rendered markdown, and the file tree.

        :return: response body, or None when the headers are already sent
        """
        path_only = url_path(self.path)
        if is_blocked(path_only):
            self.send_error(HTTPStatus.NOT_FOUND)
            return None
        if path_only in {"/", "/index.html"}:
            self.path = "/druk/start.html"
            return super().send_head()
        if path_only in {"/katalog", "/katalog/"}:
            return self.list_directory(str(CAMPAIGN_ROOT))
        if path_only.endswith(".md") and not wants_source(self.path):
            disk = Path(self.translate_path(path_only))
            if disk.is_file():
                return self.markdown_view(disk, path_only)
        return super().send_head()

    def markdown_view(self, disk: Path, path_only: str) -> io.BytesIO | None:
        """Wrap a markdown file in a page that renders it in the browser.

        :param disk: file on disk
        :param path_only: URL path without a query string
        :return: HTML page, or None when the file cannot be read
        """
        try:
            text = disk.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            self.send_error(HTTPStatus.NOT_FOUND)
            return None
        folder = path_only.rsplit("/", 1)[0]
        if folder == "":
            folder = "/"
        else:
            folder += "/"
        page = (
            "<!DOCTYPE html>\n"
            '<html lang="pl">\n'
            "<head>\n"
            '<meta charset="utf-8">\n'
            f"<title>{html.escape(disk.name)}</title>\n"
            '<link rel="stylesheet" href="/druk/podglad.css">\n'
            "</head>\n"
            "<body>\n"
            '<p class="bar">'
            '<a href="/">Start</a> · '
            f'<a href="{html.escape(folder)}">Folder</a> · '
            '<a href="/katalog">Katalog</a> · '
            '<a href="?zrodlo=1">Źródło</a>'
            "</p>\n"
            f'<textarea id="src" hidden>{html.escape(text)}</textarea>\n'
            '<article id="doc"></article>\n'
            '<script src="/druk/markdown.js"></script>\n'
            "<script>\n"
            'document.getElementById("doc").innerHTML = '
            'renderMarkdown(document.getElementById("src").value);\n'
            "</script>\n"
            "</body>\n"
            "</html>\n"
        )
        return self.send_html(page)

    def list_directory(self, path: str) -> io.BytesIO | None:
        """List a folder, skipping hidden names.

        :param path: folder on disk
        :return: HTML listing, or None when the folder cannot be read
        """
        try:
            names = sorted(Path(path).iterdir(), key=lambda item: item.name.lower())
        except OSError:
            self.send_error(HTTPStatus.NOT_FOUND)
            return None
        catalog = url_path(self.path) in {"/katalog", "/katalog/"}
        title = "Struktura kampanii" if catalog else url_path(self.path)
        rows = [
            "<!DOCTYPE html>",
            '<html lang="pl">',
            "<head>",
            '<meta charset="utf-8">',
            f"<title>{html.escape(title)}</title>",
            '<link rel="stylesheet" href="/druk/podglad.css">',
            "</head>",
            "<body>",
            f"<h1>{html.escape(title)}</h1>",
        ]
        if catalog:
            rows.append('<p class="bar"><a href="/">Start</a> · <a href="/druk/">Wydruki</a></p>')
        else:
            rows.append('<p class="bar"><a href="/">Start</a> · <a href="../">..</a></p>')
        rows.append("<ul>")
        for item in names:
            if is_hidden(item.name):
                continue
            suffix = "/" if item.is_dir() else ""
            label = item.name + suffix
            if catalog:
                href = "/" + urllib.parse.quote(label)
            else:
                href = urllib.parse.quote(label)
            rows.append(f'<li><a href="{href}">{html.escape(label)}</a></li>')
        rows.extend(["</ul>", "</body>", "</html>"])
        return self.send_html("\n".join(rows))

    def send_html(self, page: str) -> io.BytesIO:
        """Send an HTML document.

        :param page: full document
        :return: body for the caller to copy
        """
        body = page.encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        return io.BytesIO(body)


def build_parser() -> argparse.ArgumentParser:
    """Return the parser for this program.

    :return: parser with the listen port
    """
    parser = argparse.ArgumentParser(description="Serve the campaign files.")
    parser.add_argument("--port", type=port_number, default=DEFAULT_PORT)
    return parser


def port_number(value: str) -> int:
    """Reject a port outside the allowed range.

    :param value: text from the command line
    :return: port number
    :raises argparse.ArgumentTypeError: when the text is not a valid port
    """
    if not value.isdigit():
        raise argparse.ArgumentTypeError(f"{value} is not a port")
    port = int(value)
    if port < 1 or port > 65535:
        raise argparse.ArgumentTypeError(f"{value} is not a port")
    return port


def wants_source(raw: str) -> bool:
    """Tell whether the request asks for the markdown source.

    :param raw: path as sent by the browser
    :return: True when the source query is present
    """
    query = urllib.parse.parse_qs(urllib.parse.urlparse(raw).query)
    return "zrodlo" in query


def url_path(raw: str) -> str:
    """Drop the query string from a request path.

    :param raw: path as sent by the browser
    :return: decoded path
    """
    return urllib.parse.unquote(raw.split("?", 1)[0])


def is_hidden(name: str) -> bool:
    """Tell whether a file name should stay off the listing.

    :param name: one path segment
    :return: True when the name is private
    """
    return name in HIDDEN_NAMES or name.startswith(".")


def is_blocked(path: str) -> bool:
    """Tell whether a URL reaches a private folder.

    :param path: URL path without a query string
    :return: True when the request must be refused
    """
    parts = [part for part in Path(path).parts if part not in {"/", "."}]
    return any(is_hidden(part) for part in parts)


def main(argv: list[str] | None = None) -> int:
    """Listen until interrupted.

    :param argv: command arguments without the program name
    :return: process exit code
    """
    try:
        return serve(argv)
    except KeyboardInterrupt:
        return 0


def serve(argv: list[str] | None) -> int:
    """Serve the campaign root and the start page.

    :param argv: command arguments without the program name
    :return: process exit code
    """
    arguments = build_parser().parse_args(argv)
    index = CAMPAIGN_ROOT / "druk" / "index.html"
    if not index.is_file():
        print("serwer.py failed: missing index.html", file=sys.stderr)
        return 1
    try:
        handler = partial(CampaignHandler, directory=str(CAMPAIGN_ROOT))
        server = ReuseServer((HOST, arguments.port), handler)
    except OSError as error:
        print(f"serwer.py failed: {error}", file=sys.stderr)
        return 1
    print(f"http://{HOST}:{arguments.port}/")
    print(f"http://{HOST}:{arguments.port}/katalog")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
