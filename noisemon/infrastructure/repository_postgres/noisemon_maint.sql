update mentions 
set document_id = documents.document_id
from documents
where mentions.document_tag = documents.document_tag ;