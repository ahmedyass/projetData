import re

input_file_path = 'pubmed.txt'
output_file_path = 'mh_data_processed.csv'

pmid_pattern = re.compile(r'^PMID- (\d+)')
mh_pattern = re.compile(r'^MH  - (.+)')

current_pmid = None
mh_terms = []

with open(input_file_path, 'r', encoding='utf-8') as infile, open(output_file_path, 'w', newline='', encoding='utf-8') as outfile:
    for line in infile:
        pmid_match = pmid_pattern.match(line)
        if pmid_match:
            if current_pmid and mh_terms:
                for mh in mh_terms:
                    outfile.write(f'{current_pmid},MH-{mh}\n')
            current_pmid = pmid_match.group(1)
            mh_terms = []
            continue
        
        mh_match = mh_pattern.match(line)
        if mh_match:
            mh_term = mh_match.group(1)
            if '/' in mh_term:
                mh_term = mh_term.split('/')[0]
            mh_terms.append(mh_term)

    if current_pmid and mh_terms:
        for mh in mh_terms:
            outfile.write(f'{current_pmid},MH-{mh}\n')