# Projet Big Data - Data Mining

## Plan
- [Projet Big Data - Data Mining](#projet-big-data---data-mining)
  - [Plan](#plan)
    - [Big Data](#big-data)
      - [XML](#xml)
        - [Extraction de fichier `articles.xml`](#extraction-de-fichier-articlesxml)
        - [BaseX](#basex)
        - [Integration en bdd](#integration-en-bdd)
      - [JSON](#json)
        - [Etraction de fichier `articles.json`](#etraction-de-fichier-articlesjson)
        - [MongoDB](#mongodb)
        - [Integration en bdd](#integration-en-bdd-1)
      - [Neo4j](#neo4j)
    - [Data Mining](#data-mining)

---

### Big Data
#### XML
##### Extraction de fichier `articles.xml`

- Téléchargement de fichier `litcovid2BioCXML.gz` à partir du FTP ***<https://ftp.ncbi.nlm.nih.gov/pub/lu/LitCovid/>***.
- Chargement du fichier en Python pour le traiter (vu l'incapabilité de base de données native XML de traiter des fichier de grande taille).
- Extraction d'un fichier `articles.xml` sous la forme :

  ```xml
  <articles>
      <article pmid="101010">
          <title>example</title>
          <abstract>abstract 1</abstract>
          <abstract>abstract 2</abstract>
      </article>
  </articles>
  ```

##### BaseX

- Chargement de fichier `articles.xml` dans la base de données BaseX
- Générer le fichier 'résultat.txt' sous la forme :
  ```txt
    pmid/ title abstract 1 abstract 2
  ```


  ```bash
    python -m venv venv
    ./venv/scripts/activate
    pip install -r requirements.txt
    python xml_data_cleaning.py
    
    docker run --name basex10 -p 8080:8080 -d quodatum/basexhttp:latest
    docker exec -it basex10 /bin/sh
        echo "your password" | basex -cPASSWORD
        exit
    docker container restart basex10
    docker cp ./queries/xquery.xq basex10:/srv/basex/data
    docker cp ./results/articles.xml basex10:/srv/basex/data
    docker exec basex10 mkdir /srv/basex/data/.dba/files
    docker exec -it basex10 basexclient
    RUN /srv/basex/data/xquery.xq
  ```

  

##### Integration en bdd

- Création de base de données `covidxml` et des tables `articles(pmid, title)` et `abstracts(pmid, abstract)`.
- Chargement de fichier `articles.xml` dans SQL Server.
- Insertion des valeurs dans les tables.

```bash
sudo docker run -e "ACCEPT_EULA=Y" -e "MSSQL_SA_PASSWORD=root@ROOT1234" -p 1433:1433 --name sql1 --hostname sql1 -d mcr.microsoft.com/mssql/server:2022-latest
docker cp ./host/articles.xml sql1:/var/opt/mssql/data
```

```sql
-- Deleting tables
DROP TABLE IF EXISTS abstracts;
DROP TABLE IF EXISTS articles;

-- Creating the articles table
CREATE TABLE articles (
    pmid INT PRIMARY KEY,
    title VARCHAR(4000)
);

-- Creating the abstracts table
CREATE TABLE abstracts (
    id INT  IDENTITY(1,1) PRIMARY KEY,
    pmid INT,
    abstract VARCHAR(4000),
    CONSTRAINT fk_pmid FOREIGN KEY(pmid) REFERENCES articles(pmid)
);

DECLARE @xmlData XML;
SELECT @xmlData = BulkColumn
FROM OPENROWSET(BULK '/var/opt/mssql/data/articles.xml', SINGLE_BLOB) AS x;

INSERT INTO articles (pmid, title)
SELECT 
    x.value('@pmid', 'INT') AS pmid,
    x.value('(title)[1]', 'VARCHAR(4000)') AS title
FROM 
    @xmlData.nodes('/articles/article') AS T(x);

-- Insert into abstracts from XML data
INSERT INTO abstracts (pmid, abstract)
SELECT DISTINCT
    x.value('@pmid', 'INT') AS pmid,
    x.value('(abstract)[1]', 'VARCHAR(4000)') AS abstract
FROM 
    @xmlData.nodes('/articles/article') AS T(x);
```
---

#### JSON
##### Etraction de fichier `articles.json`

- Téléchargement de fichier `litcovid2BioCJSON.gz` à partir du FTP ***<https://ftp.ncbi.nlm.nih.gov/pub/lu/LitCovid/>***.
- Chargement du fichier en Python pour le traiter (vu l'incapabilité la grande taille de fichier et de nombre important des anomalies).
- Extraction d'un fichier `articles.json` sous la forme :
  ```json
  
  { "pmid" : 101010, "title" : "example", "abstracts" : [{"abstract" : "abstract 1"}, {"abstract" : "abstract 2"}]}
  { "pmid" : 101010, "title" : "example", "abstracts" : [{"abstract" : "abstract 1"}, {"abstract" : "abstract 2"}]}
  { "pmid" : 101010, "title" : "example", "abstracts" : [{"abstract" : "abstract 1"}, {"abstract" : "abstract 2"}]}
  ```

  ```bash
    python json_data_cleaning.py
    docker run --name bigmongo -v C:/Users/admin/Documents/M2/DataMining/Final/results/json_files:/data/dbfiles -d mongo
    docker exec -it bigmongo mongoimport --db projet --collection covid --file /data/dbfiles/articles.json
    docker exec -it bigmongo mongosh
      use projet
      db.getCollectionNames().forEach(function(collection) { print(collection + ": " + db[collection].count()); });
  ```

##### MongoDB

- Chargement de fichier `articles.json` dans MondoDB
- Générer le fichier 'résultat.txt' sous la forme :
  ```txt
    pmid/ title abstract 1 abstract 1
  ```

##### Integration en bdd

- Création de base de données `covidjson` et des tables `articles(pmid, title)` et `abstracts(pmid, abstract)`.
- Chargement de fichier `articles.json` dans SQL Server.
- Insertion des valeurs dans les tables.

```sql
-- Deleting tables
DROP TABLE IF EXISTS abstracts;
DROP TABLE IF EXISTS articles;

-- Creating the articles table
CREATE TABLE articles (
    pmid INT PRIMARY KEY,
    title VARCHAR(4000)
);

-- Creating the abstracts table
CREATE TABLE abstracts (
    id INT  IDENTITY(1,1) PRIMARY KEY,
    pmid INT,
    abstract VARCHAR(4000),
    CONSTRAINT fk_pmid FOREIGN KEY(pmid) REFERENCES articles(pmid)
);

DECLARE @jsonData NVARCHAR(MAX);

-- Load the preprocessed JSON data into the variable (make sure the path points to the processed JSON file)
SELECT @jsonData = BulkColumn
FROM OPENROWSET(BULK N'/var/opt/mssql/data/articles_processed.json', SINGLE_CLOB) AS j;

-- Insert data into the articles table
-- Assuming each pmid is unique for simplification, otherwise, you'll need to handle duplicates appropriately
INSERT INTO articles (pmid, title)
SELECT pmid, title
FROM OPENJSON(@jsonData)
WITH (
    pmid INT '$.pmid',
    title NVARCHAR(4000) '$.title'
);

-- Insert data into the abstracts table
INSERT INTO abstracts (pmid, abstract)
SELECT pmid, abstract
FROM OPENJSON(@jsonData)
WITH (
    pmid INT,
    abstracts NVARCHAR(MAX) AS JSON
) AS article
CROSS APPLY OPENJSON(article.abstracts)
WITH (
    abstract NVARCHAR(4000)
) AS abstract_detail;
```

---

#### Neo4j

```bash
docker run \
  --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -d \
  -v $HOME/neo4j/data:/data \
  -v $HOME/neo4j/logs:/logs \
  -v ./host:/var/lib/neo4j/import \
  -e NEO4J_AUTH=neo4j/your_password \
  -e NEO4JLABS_PLUGINS='["apoc"]' \
  -e NEO4J_apoc_export_file_enabled=true \
  -e NEO4J_apoc_import_file_enabled=true \
  -e NEO4J_apoc_import_file_use__neo4j__config=true \
  neo4j


docker exec -it neo4j bash
cypher-shell -u neo4j -p your_password

cypher-shell -u neo4j -p your_password < query.cypher
```

---

### Data Mining
- Extraction des règles d'association
