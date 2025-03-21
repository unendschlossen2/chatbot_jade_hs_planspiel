# import string
import re



chunk_index = 0
keyword_index = 0
metadata_topology = list()

class Chunk:

    def __init__(self):
        print("New chunk created")
        global chunk_index
        global keyword_index
        global metadata_topology
        self.text = ""
        self.title = ""
        self.metadata = dict()
        self.chunk_index = chunk_index
        self.keyword_index = keyword_index
        metadata_topology.append(list())
        chunk_index += 1
        keyword_index = 0

    def add_text(self, text):
        self.text += text

    def add_metadata_header(self, metadata, title_depth=0):
        metadata = metadata.strip('#').strip()
        print(f"Metadata added to chunk: {self.chunk_index} :-- {((title_depth * 'Sub') + 'Heading')}: {metadata}")
        self.metadata.update({((title_depth * "Sub") + "Heading-" + str(metadata).split(' ')[0]): metadata})

    def add_metadata_bold(self, metadata):
        metadata = metadata.strip('**').strip()
        print(f"Metadata added to chunk: {self.chunk_index} :-- Keyword: {metadata}")
        self.metadata.update({"Keyword " + str(self.keyword_index): metadata})
        self.keyword_index += 1

    def append_chunk(self):
        chunk_splitter(self)
        chunks.append(self)

    def read_text(self):
        return self.text

    def read_text_length(self):
        return len(self.text)

    def read_metadata(self):
        return self.metadata

    def read_metadata_index(self, index):
        return self.metadata[index]

    def __delete__(self, instance):
        print(f"Chunk {self.chunk_index} deleted")
        del self

    def __str__(self):
        return f"Text for Chunk: {self.chunk_index}:-- {self.text}, Metadata for Chunk: {self.chunk_index}:-- {self.metadata}"

# noinspection PyUnboundLocalVariable
def header_logic(text):
    global chunk_index
    global metadata_topology
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
            metadata_topology[current_chunk.chunk_index].append(title_depth)
            current_chunk.add_metadata_header(line, title_depth)
        elif line.startswith('---'):
            current_chunk.append_chunk()
        current_chunk.add_text(line.strip().strip('#').strip('0123456789'))

def bold_logic():
    for chunk_x in chunks:
        bold_word_collection = re.findall(r'\*\*(.*?)\*\*', chunk_x.text)
        if bold_word_collection:
            print(f"Bold words found in chunk {chunk_x.chunk_index}: {bold_word_collection}")
            for bold_word in bold_word_collection:
                chunk_x.add_metadata_bold(bold_word)
        else:
            print(f"No bold words found in chunk {chunk_x.chunk_index}")

def chunk_splitter(current_chunk):
    if current_chunk.read_text_length() > 10000:
        print(f"Chunk {current_chunk.chunk_index} is too long, splitting...")
        for depth_level in range(0,5):
            for topology_index in metadata_topology[current_chunk.chunk_index]:
                if topology_index <= depth_level:
                    while True:
                        try:
                            if topology_index in metadata_topology[current_chunk.chunk_index][metadata_topology[current_chunk.chunk_index].index(topology_index) + 1:]:
                                heading = list(current_chunk.read_metadata())[metadata_topology[current_chunk.chunk_index].index(topology_index)]
                                print(f"Splitting chunk {current_chunk.chunk_index} at heading {heading}")
                                if current_chunk.read_text().find(heading):
                                    print(f"Trying to split chunk {current_chunk.chunk_index} at heading {heading}")
                                    new_chunk = Chunk()
                                    new_chunk.add_text(list(current_chunk.read_text())[list(current_chunk.read_text()).index(current_chunk.read_text().find(heading)):])
                                    if new_chunk.read_text_length() > 10000:
                                        print(f"New chunk {new_chunk.chunk_index} is still too long, trying again...")
                                        new_chunk.__delete__(new_chunk)
                                        continue
                                    else:
                                        print(f"New chunk {new_chunk.chunk_index} created successfully")
                                        break
                        except ValueError:
                            print(f"ValueError: {topology_index} not found in metadata topology")
                            break
                        else:
                            break

                    ##### TODO: Add logic to handle the new chunk and append it to the chunks list with all metadata and text, then split old chunk to contain only the text before the heading
                    ##### TODO: Add logic so loop stops running after first successful split

def process_text(text):
    header_logic(text)
    bold_logic()

chunks = []

if __name__ == '__main__':

    with open('wiki_Data/Topsim Handbuch Markdown.md', 'r', encoding='utf-8') as file:
        sample_text = file.read()

    process_text(sample_text)
    for chunk in chunks:
        print(chunk.read_metadata())
        print(chunk.read_text_length())
    print(metadata_topology)