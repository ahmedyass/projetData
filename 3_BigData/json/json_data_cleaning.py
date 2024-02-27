import ujson as json
import time
import tracemalloc

input_file_path = './litcovid2BioCJSON.json'
output_file_path = './results/articles.json'

def is_valid_json_line(line):
    return not line.strip().startswith('<!DOCTYPE html>') and not line.strip() in ('[', ']', ']]', '[[')

def process_line(line):
    try:
        cleaned_line = line.strip().lstrip(',[').rstrip(',]')
        article_data = json.loads(cleaned_line)
        return article_data
    except Exception as e:
        print(f"Error processing line: {e}")
        return None

def create_article_structure(article_data):
    try:
        article = {
            'pmid': article_data['passages'][0]['infons'].get('article-id_pmid'),
            'title': article_data['passages'][0]['text'],
            'abstracts': [{'abstract': p['text']} for p in article_data['passages'] if p['infons'].get('section_type') == 'ABSTRACT' and p['infons'].get('type') == 'abstract']
        }
        return article
    except Exception as e:
        print("Error creating article structure:", e)
        return None

def process_file(input_path, output_path):
    tracemalloc.start()
    start_time = time.time()
    article_count = 0

    with open(input_path, 'r', encoding='utf-8') as file, open(output_path, 'w', encoding='utf-8') as outfile:
        for i, line in enumerate(file):
            if i < 3:  # Skip the first 3 lines
                continue
            if line == ']]':  # Check for the end of the file
                break
            if is_valid_json_line(line):
                article_data = process_line(line)
                if article_data:
                    structured_article = create_article_structure(article_data)
                    if structured_article:
                        json.dump(structured_article, outfile)
                        outfile.write('\n')  # New line for next JSON object
                        article_count += 1

    end_time = time.time()
    memory_usage = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    print(f"\nProcessed {article_count} articles.")
    print(f"Execution time: {end_time - start_time} seconds")
    print(f"Memory usage: {memory_usage[1] - memory_usage[0]} bytes")

if __name__ == "__main__":
    process_file(input_file_path, output_file_path)
