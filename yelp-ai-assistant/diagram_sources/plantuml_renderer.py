"""
PlantUML Renderer
=================

Uses the ``plantuml`` Python library to:

  1. Encode ``.puml`` source files into the compressed PlantUML URL format.
  2. Build render URLs pointing to the public PlantUML server
     (https://www.plantuml.com/plantuml) — no local server required.
  3. Optionally download the rendered PNG/SVG when network access is
     available.

URL encoding is pure-local (compression + base64); it never makes a
network call on its own.  Downloading the rendered image is optional.

Usage
-----
    from diagrams.plantuml_renderer import PlantUMLRenderer

    renderer = PlantUMLRenderer()

    # Get a shareable URL for a .puml file
    url = renderer.url_for_file("diagrams/plantuml/component_architecture.puml")
    print(url)

    # Download rendered PNG (requires network access)
    renderer.save_png("diagrams/plantuml/sequence_query_flow.puml", "/tmp/out.png")
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

import plantuml


# Default PlantUML public server — change to a self-hosted instance if needed
DEFAULT_SERVER_URL: str = "https://www.plantuml.com/plantuml/img/"
DEFAULT_SVG_URL: str = "https://www.plantuml.com/plantuml/svg/"


class PlantUMLRenderer:
    """
    Encodes PlantUML source into server render URLs and optionally
    downloads rendered images.

    Parameters
    ----------
    server_url : base URL of the PlantUML server (PNG endpoint)
    svg_url    : base URL of the PlantUML server (SVG endpoint)
    """

    def __init__(
        self,
        server_url: str = DEFAULT_SERVER_URL,
        svg_url: str = DEFAULT_SVG_URL,
    ):
        self._png_client = plantuml.PlantUML(url=server_url)
        self._svg_client = plantuml.PlantUML(url=svg_url)

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------

    def encode(self, source: str) -> str:
        """
        Return the compressed, base64-encoded representation of *source*.

        This is a pure-local operation — no network call.
        """
        return plantuml.deflate_and_encode(source)

    def url_for_source(self, source: str, fmt: str = "png") -> str:
        """
        Build a render URL for raw PlantUML *source* text.

        Parameters
        ----------
        source : PlantUML diagram source (must start with ``@startuml``).
        fmt    : ``"png"`` or ``"svg"``
        """
        encoded = self.encode(source)
        client = self._svg_client if fmt == "svg" else self._png_client
        return client.get_url(source)

    def url_for_file(self, path: str, fmt: str = "png") -> str:
        """
        Build a render URL for a ``.puml`` file on disk.

        Parameters
        ----------
        path : path to the ``.puml`` file (absolute or relative to CWD)
        fmt  : ``"png"`` or ``"svg"``
        """
        source = Path(path).read_text(encoding="utf-8")
        return self.url_for_source(source, fmt=fmt)

    def save_png(self, puml_path: str, out_path: str) -> bool:
        """
        Download the rendered PNG from the PlantUML server and save it.

        Returns True on success, False if the download fails (e.g. no
        network access).

        Parameters
        ----------
        puml_path : path to the ``.puml`` source file
        out_path  : destination path for the rendered PNG
        """
        source = Path(puml_path).read_text(encoding="utf-8")
        try:
            self._png_client.processes_file(
                filename=puml_path,
                outfile=out_path,
            )
            return True
        except Exception:   # noqa: BLE001
            return False

    def render_all(
        self,
        puml_dir: str,
        out_dir: str,
        fmt: str = "png",
    ) -> dict[str, str]:
        """
        Render every ``.puml`` file in *puml_dir* and return a mapping of
        ``{stem: url}`` for each diagram.

        When *out_dir* is provided, also attempts to download rendered images.

        Parameters
        ----------
        puml_dir : directory containing ``.puml`` source files
        out_dir  : directory to write rendered images (created if absent)
        fmt      : ``"png"`` or ``"svg"``
        """
        os.makedirs(out_dir, exist_ok=True)
        urls: dict[str, str] = {}
        for entry in sorted(Path(puml_dir).glob("*.puml")):
            url = self.url_for_file(str(entry), fmt=fmt)
            urls[entry.stem] = url
            # Best-effort download
            if fmt == "png":
                out_file = os.path.join(out_dir, f"{entry.stem}.png")
                self.save_png(str(entry), out_file)
        return urls


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def _cli() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description="Encode PlantUML source files and print render URLs."
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=os.path.join(os.path.dirname(__file__), "plantuml"),
        help="Path to a single .puml file or a directory of .puml files",
    )
    parser.add_argument(
        "--fmt",
        choices=("png", "svg"),
        default="png",
        help="Output format (default: png)",
    )
    parser.add_argument(
        "--out-dir",
        default="/tmp/plantuml_out",
        help="Directory for rendered images (default: /tmp/plantuml_out)",
    )
    args = parser.parse_args()

    renderer = PlantUMLRenderer()

    target = Path(args.path)
    if target.is_file():
        url = renderer.url_for_file(str(target), fmt=args.fmt)
        print(f"{target.name}: {url}")
    elif target.is_dir():
        urls = renderer.render_all(str(target), args.out_dir, fmt=args.fmt)
        for name, url in urls.items():
            print(f"{name}: {url}")
    else:
        parser.error(f"Path not found: {args.path}")


if __name__ == "__main__":
    _cli()
