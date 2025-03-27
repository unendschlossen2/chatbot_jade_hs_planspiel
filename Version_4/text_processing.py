import re

'''
This script processes a markdown file, splitting it into chunks based on headers and bold keywords.
It creates a list of Chunk objects, each containing text and metadata.
The script also handles chunk splitting if the text exceeds a certain length.
'''

chunks = []
chunk_index = 0
keyword_index = 0
minimum_chunk_chars = 1000
maximum_chunk_chars = 3000
filepath = 'wiki_Data/Topsim Handbuch Markdown.md'

class Chunk:

    def __init__(self):
        global chunk_index
        global keyword_index
        self.text = ""
        self.metadata = dict()
        self.chunk_index = chunk_index
        self.keyword_index = keyword_index
        self.parent_header = dict()
        print("New chunk created, index:", chunk_index)
        keyword_index = 0
        chunk_index += 1

    def append_parent_header(self, header_key, header_value):
        self.parent_header[header_key] = header_value

    def read_parent_header(self):
        return self.parent_header

    def add_text(self, text):
        self.text += text

    def add_metadata_header(self, metadata, title_depth=0):
        metadata = metadata.strip('#').strip()
       # print(f"Metadata added to chunk: {self.chunk_index} :-- {((title_depth * 'Sub') + 'Heading')}: {metadata}")
        self.metadata.update({((title_depth * "Sub") + "Heading-" + str(metadata).split(' ')[0]): metadata})

    def add_metadata_bold(self, metadata):
        metadata = metadata.strip('**').strip()
       # print(f"Metadata added to chunk: {self.chunk_index} :-- Keyword: {metadata}")
        self.metadata.update({"Keyword-" + str(self.keyword_index): metadata})
        self.keyword_index += 1

    def append_chunk(self):
        if self.read_text_length() > maximum_chunk_chars:
            new_chunk = chunk_splitter(self)
            chunks.append(self)
            new_chunk.append_chunk()
        else:
            chunks.append(self)

    def copy_metadata(self, metadata_index):
        new_metadata = dict()
        index_reached = False
        for meta_key, meta_value in self.metadata.items():
            if meta_key == metadata_index:
                index_reached = True
            if index_reached:
                new_metadata.update({meta_key: meta_value})
        return new_metadata

    def copy_text(self, split_index):
        if maximum_chunk_chars> len(self.text[:split_index]) > minimum_chunk_chars:
            new_text = self.text[split_index:]
            self.text = self.text[:split_index]
            print("TEXT SPLIT:", new_text)
            return new_text
        else:
            print("TEXT NOT SPLIT", len(self.text[:split_index]))
            return ""

    def read_text(self):
        return self.text

    def read_text_length(self):
        return len(self.text)

    def read_metadata(self):
        return self.metadata

    def read_metadata_index(self, key):
        return self.metadata.get(key)

    def __delete__(self):
        global chunk_index
        print(f"Chunk {self.chunk_index} deleted")
        del self
        chunk_index -= 1

    def __str__(self):
        return f"Text for Chunk: {self.chunk_index}:-- {self.text}, Metadata for Chunk: {self.chunk_index}:-- {self.metadata}"


def read_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
        return text

# noinspection PyUnboundLocalVariable
def header_logic(text):
    global chunk_index
    table = False
    table_text = []
    for line in text.splitlines():
        if line.startswith('#'):
            title_depth = -1
            if not line.startswith('###'):
                try:
                    current_chunk.append_chunk()
                    current_chunk = Chunk()
                except UnboundLocalError:
                    current_chunk = Chunk()
            for x in line:
                if x == "#":
                    title_depth += 1
            current_chunk.add_metadata_header(line, title_depth)
            if not table:
                current_chunk.add_text(line.strip().strip('#').strip('0123456789')+':')
        elif line.startswith('|'):
            table_text.append(line)
            table = True
        elif line.startswith('---'):
            current_chunk.append_chunk()
        if table and not line.startswith('|'):
            table = False
            current_chunk.add_text(parse_table_to_string(table_text))
            table_text = []
        if not table and not line.startswith('#') and not line.startswith('---'):
            current_chunk.add_text(line.strip().strip('#').strip('0123456789')+' ')


def bold_logic():
    for current_chunk in chunks:
        bold_word_collection = re.findall(r'\*\*(.*?)\*\*', current_chunk.read_text())
        if bold_word_collection:
            for bold_word in bold_word_collection:
                current_chunk.add_metadata_bold(bold_word)


def parse_table_to_string(markdown_table):
    parsed_table_text = 'TABELLE: '
    lines = markdown_table
    if len(lines) < 3:
        print("Table is too short")
        return

    header = [h.strip() for h in re.split(r'\|', lines[0])[1:-1]]
    separator = lines[1].strip()
    if not all(c in ['-', ':', '|', ' '] for c in separator):
        print("Invalid table separator")
        return

    data_rows = []
    for line in lines[2:]:
        row_data = [d.strip() for d in re.split(r'\|', line)[1:-1]]
        if len(row_data) == len(header):
            data_rows.append(row_data)

    output_strings = []
    for row in data_rows:
        if len(header) == 2:
            output_strings.append(f"{header[0]}: {row[0]}, {header[1]}: {row[1]},")
        else:
            output_strings.append(", ".join([f"{header[i]}: {row[i]}" for i in range(len(header))]))
    parsed_table_text += ', '.join(output_strings)

    return parsed_table_text + ', TABELLENENDE.'


def chunk_splitter(current_chunk):
    print(f'Chunk {current_chunk.chunk_index} is too long with {current_chunk.read_text_length()} chars, attempting to split...')
    for header_level in range(1, 5):
        possible_splits = [key for key in current_chunk.metadata.keys() if key.startswith('Sub') and key.split('Heading')[0].split('Sub').count('')-1 == header_level]
        possible_splits.reverse()
        print(possible_splits)
        for possible_split in possible_splits:
            new_chunk = Chunk()
            #new_chunk.metadata.update(current_chunk.read_parent_header()) #TODO ADD PARENT HEADER METADATA LOGIC
            new_chunk.metadata.update(current_chunk.copy_metadata(possible_split))
            print(current_chunk.read_text())
            new_chunk.text = current_chunk.copy_text(current_chunk.read_text().find(current_chunk.read_metadata_index(possible_split)))
            print(new_chunk.read_text())
            print(current_chunk.read_text_length())
            if maximum_chunk_chars > current_chunk.read_text_length() > minimum_chunk_chars:
                print(f"Chunk {current_chunk.chunk_index} is now {current_chunk.read_text_length()} chars long, and {new_chunk.chunk_index} is {new_chunk.read_text_length()} chars long")
                return new_chunk
            else:
                print(f"Chunk {current_chunk.chunk_index} is too long with {current_chunk.read_text_length()}, trying next header level on {header_level}")
                new_chunk.__delete__()


def process_text():
    header_logic(text=read_file(filepath))
    bold_logic()
    return chunks


if __name__ == '__main__':
    sample_text = read_file(filepath)
    process_text()
    print(chunks)
    text_length = 0
    for chunk in chunks:
        print("chunk index:", chunk.chunk_index)
        print(chunk.metadata)
        print("chunk länge:", chunk.read_text_length())
        text_length += chunk.read_text_length()
    print(f'Original text length: {len(sample_text)}, chunked text length: {text_length}, "#" count: {sample_text.count("#")}')