"""Generate PDF dossiê from markdown using Playwright (Chromium)."""
import logging
import tempfile
from pathlib import Path
from typing import Optional

import markdown

logger = logging.getLogger(__name__)

_CSS = """
body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif; line-height: 1.6; margin: 2cm; color: #1a2138; }
h1 { color: #4285F4; border-bottom: 2px solid #4285F4; padding-bottom: 8px; }
h2 { color: #1a2138; margin-top: 1.8em; border-bottom: 1px solid #e5e7eb; padding-bottom: 4px; }
h3 { color: #1a2138; margin-top: 1.5em; }
strong { color: #0f172a; }
em { color: #475569; }
code { background: #f1f5f9; padding: 2px 6px; border-radius: 3px; font-size: 0.9em; }
blockquote { border-left: 3px solid #4285F4; padding: 0.5em 1em; background: #f8fafc; margin: 1em 0; }
table { border-collapse: collapse; width: 100%; margin: 1em 0; }
th, td { border: 1px solid #e5e7eb; padding: 8px 12px; text-align: left; }
th { background: #f1f5f9; }
ul, ol { margin: 0.5em 0; padding-left: 1.5em; }
li { margin: 0.25em 0; }
hr { border: none; border-top: 1px solid #e5e7eb; margin: 2em 0; }
.badge { display: inline-block; padding: 2px 8px; border-radius: 99px; font-size: 0.85em; font-weight: 600; }
.badge.falso { background: #fee; color: #c33; }
.badge.verdadeiro { background: #efe; color: #3a3; }
.balse.enganoso { background: #ffe; color: #a83; }
"""


def _md_to_html(md: str) -> str:
    return markdown.markdown(md, extensions=["tables", "fenced_code"])


def _render_pdf_playwright(full_html: str, output_path: Optional[str]) -> bytes:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch()
        try:
            page = browser.new_page()
            page.set_content(full_html, wait_until="load")
            if output_path:
                page.pdf(
                    path=output_path,
                    format="A4",
                    margin={"top": "20mm", "right": "20mm", "bottom": "20mm", "left": "20mm"},
                    print_background=True,
                )
                return Path(output_path).read_bytes()
            pdf_bytes = page.pdf(
                format="A4",
                margin={"top": "20mm", "right": "20mm", "bottom": "20mm", "left": "20mm"},
                print_background=True,
            )
            return pdf_bytes
        finally:
            browser.close()


def gerar_dossie_pdf(dossie_md: str, output_path: Optional[str] = None) -> bytes:
    html = _md_to_html(dossie_md)
    full_html = f"<html><head><meta charset='utf-8'><style>{_CSS}</style></head><body>{html}</body></html>"

    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    try:
        return _render_pdf_playwright(full_html, output_path)
    except Exception as e:
        logger.warning(f"Playwright PDF falhou ({e}); tentando WeasyPrint")
        try:
            from weasyprint import HTML
            if output_path:
                HTML(string=full_html).write_pdf(output_path)
                return Path(output_path).read_bytes()
            return HTML(string=full_html).write_pdf()
        except Exception as e2:
            logger.error(f"WeasyPrint tambem falhou: {e2}")
            raise NotImplementedError(
                f"PDF generation failed. Playwright error: {e}. WeasyPrint error: {e2}"
            ) from e2
