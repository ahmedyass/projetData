import xml.etree.ElementTree as ET
from lxml import etree
import time
import tracemalloc

def process_document(elem):
    d = {}
    for passage in elem.findall('.//passage'):
        article_id_pmid = passage.find("infon[@key='article-id_pmid']")
        if article_id_pmid is not None:
            d['pmid'] = article_id_pmid.text

        section_type = passage.find("infon[@key='section_type']")
        if section_type is not None and section_type.text == 'TITLE':
            title_text = passage.find('text')
            if title_text is not None:
                d['title'] = title_text.text

        elif section_type is not None and section_type.text == 'ABSTRACT':
            abstract_text = passage.find('text')
            if abstract_text is not None:
                if 'abstract' not in d:
                    d['abstract'] = []
                d['abstract'].append(abstract_text.text)

    return d

def write_to_file(root, output_file):
    tree = ET.ElementTree(root)
    tree.write(output_file)

def main():
    file_path = './litcovid2BioCXML.xml'
    output_file = './results/articles.xml'

    tracemalloc.start()
    start_time = time.time()

    _root = ET.Element("articles")
    context = etree.iterparse(file_path, events=('end',), tag='document')
    article_count = 0

    for event, elem in context:
        document_data = process_document(elem)
        if document_data:
            article = ET.SubElement(_root, "article", pmid=document_data.get("pmid", ""))

            title = ET.SubElement(article, "title")
            title.text = document_data.get("title", "")

            for abstract_text in document_data.get("abstract", []):
                abstract = ET.SubElement(article, "abstract")
                abstract.text = abstract_text

            article_count += 1

        elem.clear()
        while elem.getprevious() is not None:
            del elem.getparent()[0]

    del context
    write_to_file(_root, output_file)

    end_time = time.time()
    memory_usage = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    print(f"Processed {article_count} articles.")
    print(f"Execution time: {end_time - start_time} seconds")
    print(f"Memory usage: {memory_usage[1] - memory_usage[0]} bytes")

if __name__ == "__main__":
    main()
