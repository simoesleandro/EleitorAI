def gerar_dossie_pdf(dossie_md: str, output_path: str | None = None) -> bytes:
    raise NotImplementedError(
        "PDF generation requires WeasyPrint, which depends on GTK system libraries. "
        "Not available in this environment. Will be enabled in Linux production deploy."
    )


def _md_to_html(md: str) -> str:
    raise NotImplementedError("Stub")
