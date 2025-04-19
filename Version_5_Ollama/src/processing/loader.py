import os
import logging
import pypdf
from typing import Callable, Dict, Optional

# Konfiguriere grundlegendes Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Hilfsfunktionen für spezifische Dateitypen ---

# --- PDF-Dateien ---

def _load_pdf(file_path: str) -> Optional[str]:
    """Lädt Textinhalt aus einer PDF-Datei."""
    if not pypdf:
        logging.error(f"pypdf ist nicht installiert. Kann PDF nicht verarbeiten: {file_path}")
        return None
    try:
        reader = pypdf.PdfReader(file_path)
        text_content = []
        for page_num, page in enumerate(reader.pages):
            try:
                text_content.append(page.extract_text())
            except Exception as e:
                logging.warning(f"Konnte Text von Seite {page_num + 1} in {file_path} nicht extrahieren: {e}")
        full_text = "\n".join(filter(None, text_content)) # Filtere leere Strings und verbinde
        logging.info(f"PDF erfolgreich geladen: {file_path}")
        return full_text
    except FileNotFoundError:
        logging.error(f"PDF-Datei nicht gefunden: {file_path}")
        return None
    except Exception as e:
        logging.error(f"Fehler beim Lesen der PDF-Datei {file_path}: {e}")
        return None

# --- generische Textdateien ---

def _load_generic_text_file(file_type: str, file_path: str) -> Optional[str]:
    """Lädt Textinhalt aus verschiedenen einfachen Textformaten."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        logging.info(f"{file_type} erfolgreich geladen: {file_path}")
        return content
    except FileNotFoundError:
        logging.error(f"{file_type} nicht gefunden: {file_path}")
        return None
    except Exception as e:
        logging.error(f"Fehler beim Lesen der {file_type} {file_path}: {e}")
        return None

# --- Mapping von Dateiendungen zu Ladefunktionen ---

# Typ-Hint für die Ladefunktionen
LoaderFunction = Callable[[str, str], Optional[str]]

# Dictionary, das Dateiendungen (lowercase) den Ladefunktionen zuordnet
LOADER_MAPPING: Dict[str, LoaderFunction] = {
    ".pdf": _load_pdf,
    ".md": _load_generic_text_file,
    ".txt": _load_generic_text_file,
    # Hier bei Bedarf weitere Mappings hinzufügen
    # z.B. ".docx": _load_docx (nach Installation & Import von python-docx)
}

# --- Haupt-Ladefunktion ---

def load_document(file_path: str) -> Optional[str]:
    """
    Lädt den Textinhalt aus einer unterstützten Datei basierend auf ihrer Endung.

    Args:
        file_path (str): Der Pfad zur Datei.

    Returns:
        Optional[str]: Der extrahierte Textinhalt als String oder None bei Fehlern
                       oder nicht unterstützten Dateitypen.

    Hinweis: Diese Funktion extrahiert nur Text. Inhalte aus Bildern werden ignoriert.
    """

    file_type = os.path.splitext(file_path)[1].lower()  # Dateityp aus dem Dateipfad extrahieren

    try:
        # Extrahiere die Dateiendung und konvertiere sie zu Kleinbuchstaben
        _, file_extension = os.path.splitext(file_path)
        file_extension = file_extension.lower()

        # Finde die passende Ladefunktion im Mapping
        loader_func = LOADER_MAPPING.get(file_extension)

        if loader_func:
            # Rufe die spezifische Ladefunktion auf
            return loader_func(file_type, file_path)
        else:
            # Gib eine Warnung aus, wenn der Dateityp nicht unterstützt wird
            logging.warning(f"Nicht unterstützter Dateityp '{file_extension}' für Datei: {file_path}")
            return None
    except Exception as e:
        # Fange unerwartete Fehler beim Laden ab
        logging.error(f"Unerwarteter Fehler beim Versuch, Datei zu laden {file_path}: {e}")
        return None

# --- Beispiel ---
if __name__ == '__main__':
    test_pdf_path = 'pfad/zu/deinem/test.pdf'
    test_md_path = 'C:/Users/peroj/IdeaProjects/chatbot_jade_hs_planspiel/Version_5_Ollama/test_files/test.md'
    test_txt_path = 'C:/Users/peroj/IdeaProjects/chatbot_jade_hs_planspiel/Version_5_Ollama/test_files/test.txt'
    test_unsupported_path = 'pfad/zu/deinem/test.jpg'

    print(f"\n--- Lade PDF: {test_pdf_path} ---")
    pdf_content = load_document(test_pdf_path)
    if pdf_content:
        print(f"Erste 500 Zeichen: {pdf_content[:500]}...")
    else:
        print("PDF konnte nicht geladen werden.")

    print(f"\n--- Lade Markdown: {test_md_path} ---")
    md_content = load_document(test_md_path)
    if md_content:
        print(f"Erste 500 Zeichen: {md_content[:500]}...")
    else:
        print("Markdown konnte nicht geladen werden.")

    print(f"\n--- Lade Text: {test_txt_path} ---")
    txt_content = load_document(test_txt_path)
    if txt_content:
        print(f"Erste 500 Zeichen: {txt_content[:500]}...")
    else:
        print("Textdatei konnte nicht geladen werden.")

    print(f"\n--- Lade nicht unterstützte Datei: {test_unsupported_path} ---")
    unsupported_content = load_document(test_unsupported_path)
    if unsupported_content is None:
        print("Nicht unterstützte Datei korrekt als 'None' behandelt.")