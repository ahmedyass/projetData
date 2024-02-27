CALL apoc.load.json("file:///articles.json") YIELD value AS q
MERGE (a:Article {pmid: q.pmid, title: q.title})
WITH a, q.abstracts AS abstracts
UNWIND abstracts AS abstract
MERGE (ab:Abstract {text: abstract.abstract})
MERGE (a)-[:HAS_ABSTRACT]->(ab);
