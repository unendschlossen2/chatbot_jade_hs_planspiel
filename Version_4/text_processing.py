import string
import re


def lowercase_text(text):
    return text.lower()

def remove_punctuation(text):
    punctuation_to_remove = string.punctuation.replace('#', '').replace('-', '') # Create punctuation string excluding '#' and '-'
    return text.translate(str.maketrans('', '', punctuation_to_remove))

def normalize_whitespace(text):
    return re.sub(r'\s+', ' ', text).strip()

def transform_markdown_headings(text):
    def replace_heading(match):
        heading_level = len(match.group(1))
        heading_text = match.group(2).strip()
        return f"Section Level {heading_level}: {heading_text}\n"

    return re.sub(r'^(#+)\s(.*)$', replace_heading, text, flags=re.MULTILINE)

def transform_markdown_table_to_plaintext(text):
    lines = text.strip().split('\n')
    if not lines:
        return ""

    header_row = None
    data_rows = []
    in_table = False
    plaintext_table_lines = []

    for line in lines:
        stripped_line = line.strip()
        if stripped_line.startswith("|"):
            in_table = True
            row_cells = [cell.strip() for cell in stripped_line.strip('|').split('|')]
            if header_row is None: # First table row is assumed to be header
                header_row = row_cells
            else:
                data_rows.append(row_cells)
        elif in_table:
            in_table = False


    if header_row:
        plaintext_table_lines.append("Tabelle:")
        plaintext_table_lines.append("Spalten: " + ", ".join(header_row))
        for i, row in enumerate(data_rows[1:]):
            plaintext_table_lines.append(f"Zeile {i+1}: " + ", ".join(row))

        return "\n".join(plaintext_table_lines)
    else:
        return text


def process_text(text):
    text = transform_markdown_table_to_plaintext(text)
    text = lowercase_text(text)
    #text = remove_punctuation(text)
    text = transform_markdown_headings(text)
    text = normalize_whitespace(text)
    return text

if __name__ == '__main__':
    sample_text = """
# This is a sample text.
## This is a subheading
This is a line with punctuation! And some special characters: @#$%^&*()
This line has     extra   spaces.
Tabelle der prozesse:
| Aktiv  | Passiv  |
|----------|----------|
| Aufräumen   | Klimaanlage   |
| Saubermachen   | Lüftung   |
"""

    processed_text = process_text(sample_text)
    print(processed_text)