CREATE EXTENSION vector;

CREATE TABLE public.entities (
	entity_qid varchar NOT NULL,
	CONSTRAINT entities_pk PRIMARY KEY (entity_qid)
);

CREATE TABLE public.documents (
	document_id varchar NOT NULL,
	raw_content varchar NULL,
	"content" varchar NULL,
	raw_text varchar NULL,
	"text" varchar NULL,
	CONSTRAINT documents_pk PRIMARY KEY (document_id)
);
CREATE UNIQUE INDEX documents_document_id_idx ON public.documents USING btree (document_id);

CREATE TABLE public.mentions (
	mention_id varchar NOT NULL,
	document_id varchar NOT NULL,
	entity_qid varchar NULL,
	span varchar NOT NULL,
	span_start int4 NOT NULL,
	span_end int4 NOT NULL,
	vector public.vector NULL,
	CONSTRAINT mentions_pk PRIMARY KEY (mention_id)
);
CREATE INDEX mentions_vector_idx ON public.mentions USING hnsw (vector vector_ip_ops);
ALTER TABLE public.mentions ADD CONSTRAINT mentions_fk FOREIGN KEY (document_id) REFERENCES public.documents(document_id) ON DELETE CASCADE;