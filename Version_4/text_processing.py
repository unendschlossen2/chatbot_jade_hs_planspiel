# import string
# import re

chunk_index = 0

class Chunk:

    def __init__(self):
        global chunk_index
        self.text = ""
        self.title = ""
        self.metadata = dict()
        self.chunk_index = chunk_index
        chunk_index += 1

    def add_text(self, text):
        self.text += text

    def add_metadata_header(self, metadata, title_depth=0):
        metadata = metadata.strip('#').strip()
        print(f"Metadata added to chunk: {self.chunk_index} :-- {metadata}")
        self.metadata.update({((title_depth * "Sub")+"Heading"): metadata})

    def read_text(self):
        return self.text

    def read_metadata(self):
        return self.metadata

    def read_metadata_index(self, index):
        return self.metadata[index]

    def __str__(self):
        return f"Text for Chunk: {self.chunk_index}:-- {self.text}, Metadata for Chunk: {self.chunk_index}:-- {self.metadata}"


# noinspection PyUnboundLocalVariable
def header_logic(text):
    global chunk_index
    for line in text.splitlines():
        if line.startswith('#'):
            title_depth = -1
            if not line.startswith('###'):
                try:
                    chunks.append(current_chunk)
                    current_chunk = Chunk()
                except UnboundLocalError:
                    current_chunk = Chunk()
                print("New chunk created")
            for x in line:
                if x == "#":
                    title_depth += 1
            current_chunk.add_metadata_header(line, title_depth)
        elif line.startswith('---'):
            chunks.append(current_chunk)

def process_text(text):
    header_logic(text)

chunks = []

if __name__ == '__main__':

    with open('wiki_Data/Topsim Handbuch Markdown.md', 'r', encoding='utf-8') as file:
        sample_text = file.read()

    process_text(sample_text)
    for chunk in chunks:
        print(chunk)