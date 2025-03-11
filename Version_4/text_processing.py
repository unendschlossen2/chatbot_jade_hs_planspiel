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
    index = []
    i = 0

    for line in lines:
        if line.startswith("|"):
            index.append(i)
        i += 1

    tabellenname = lines[index[0]-1].strip()

    print(index)

    if not lines:
        return ""

    header_row = lines[index[0]].strip('|').split('|') # Remove leading/trailing pipes and split
    data_rows = [line.strip('|').split('|') for line in lines[index[2]:]] # Skip separator line

    plaintext_table = tabellenname + "\n"

    # Header row
    plaintext_table += "Spalten: " + ", ".join([h.strip() for h in header_row]) + "\n"

    # Data rows
    for i, row in enumerate(data_rows):
        plaintext_table += f"Zeile {i+1}: " + ", ".join([cell.strip() for cell in row]) + "\n"

    return plaintext_table

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