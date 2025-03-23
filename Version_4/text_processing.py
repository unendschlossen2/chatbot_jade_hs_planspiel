# import string
import re



chunk_index = 0
keyword_index = 0
minimum_chunk_chars = 1000
maximum_chunk_chars = 5000

class Chunk:

    def __init__(self):
        global chunk_index
        global keyword_index
        self.text = ""
        self.title = ""
        self.metadata = dict()
        self.chunk_index = chunk_index
        self.keyword_index = keyword_index
        print("New chunk created, index:", chunk_index)
        keyword_index = 0
        chunk_index += 1

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

# noinspection PyUnboundLocalVariable
def header_logic(text):
    global chunk_index
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
        elif line.startswith('---'):
            current_chunk.append_chunk()
        current_chunk.add_text(line.strip().strip('#').strip('0123456789')+':')

def bold_logic():
    for current_chunk in chunks:
        bold_word_collection = re.findall(r'\*\*(.*?)\*\*', current_chunk.read_text())
        if bold_word_collection:
            for bold_word in bold_word_collection:
                current_chunk.add_metadata_bold(bold_word)
        else:
            pass

def chunk_splitter(current_chunk):
    print(f'Chunk {current_chunk.chunk_index} is too long with {current_chunk.read_text_length()} chars, attempting to split...')
    for header_level in range(1, 5):
        possible_splits = [key for key in current_chunk.metadata.keys() if key.startswith('Sub') and key.split('Heading')[0].split('Sub').count('')-1 == header_level]
        possible_splits.reverse()
        print(possible_splits)
        for possible_split in possible_splits:
            new_chunk = Chunk()
            new_chunk.metadata = current_chunk.copy_metadata(possible_split)
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

def process_text(text):
    header_logic(text)
    bold_logic()

chunks = []

if __name__ == '__main__':

    with open('wiki_Data/Topsim Handbuch Markdown.md', 'r', encoding='utf-8') as file:
        sample_text = file.read()
    process_text(sample_text)
    print(chunks)
    text_length = 0
    for chunk in chunks:
        print("chunk index:", chunk.chunk_index)
        print("chunk länge:", chunk.read_text_length())
        text_length += chunk.read_text_length()
    print(f'Original text length: {len(sample_text)}, chunked text length: {text_length}')
    print(f'Cut text: {''.join(sorted(set(sample_text) - set(''.join(chunk.read_text() for chunk in chunks))))}')