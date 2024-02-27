xquery version "3.1";

let $filePath := "./basex/data/.dba/files/resultat.txt"

let $_ := file:write($filePath, '') (: Clear the file before appending :)

for $article in collection("/srv/basex/data/articles.xml")//article
let $pmid := $article/@pmid/string()
let $title := $article/title/string()
let $head := string-join(($pmid, $title), '/')
let $abstracts := string-join($article/abstract/text(), ' ')
let $line := string-join(($head, $abstracts), ' ')
return file:append($filePath, $line || '&#10;')