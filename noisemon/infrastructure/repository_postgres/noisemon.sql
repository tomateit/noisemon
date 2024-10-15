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

CREATE TABLE public.narratives (
	narrative_id uuid NOT NULL,
	narrative_name varchar NOT NULL,
	narrative_context varchar NOT NULL,
	created_at timestamptz NOT NULL,
	CONSTRAINT narrative_pk PRIMARY KEY (narrative_id)
);

CREATE TABLE public.narrative_statement (
	narrative_statement_id uuid NOT NULL,
	narrative_id uuid NOT NULL,
	statement_text varchar NOT NULL,
	created_at timestamptz NOT NULL,
	CONSTRAINT narrative_statement_pk PRIMARY KEY (narrative_statement_id),
	CONSTRAINT narrative_statement_narrative_fk FOREIGN KEY (narrative_id) REFERENCES public.narratives(narrative_id) ON DELETE CASCADE
);

CREATE TABLE public.telegram_messages (
	id uuid NOT NULL,
	channel_id uuid NOT NULL,
	telegram_message_id int NOT NULL,
	telegram_channel_id int NULL,
	telegram_user_id int NULL,
	"content" varchar NULL,
	"timestamp" timestamptz NOT NULL,
	created_at timestamptz NOT NULL,
	CONSTRAINT telegram_message_pk PRIMARY KEY (id)
);
ALTER TABLE public.telegram_messages ADD has_been_processed boolean DEFAULT false NOT NULL;
ALTER TABLE public.telegram_messages ADD CONSTRAINT telegram_message_telegram_channel_fk FOREIGN KEY (channel_id) REFERENCES public.telegram_channels(id) ON DELETE CASCADE;
ALTER TABLE public.telegram_messages ADD CONSTRAINT unique_channel_and_message_id UNIQUE (channel_id,telegram_message_id);
ALTER TABLE public.telegram_messages ADD retrieval_timestamp timestamptz NOT NULL;
CREATE INDEX telegram_message_telegram_channel_id_idx ON public.telegram_messages (telegram_channel_id);

CREATE TABLE public.tasks (
	task_id uuid NOT NULL,
	complete bool DEFAULT false NOT NULL,
	created_at timestamptz NOT NULL,
	request jsonb NOT NULL,
	CONSTRAINT task_pk PRIMARY KEY (task_id)
);
ALTER TABLE public.tasks ADD is_accepted_for_polling boolean DEFAULT false NOT NULL;

CREATE TABLE public.document_fragments (
	fragment_id uuid NOT NULL,
	document_id uuid NOT NULL,
	"content" text NOT NULL,
	"index" int NOT NULL,
	created_at timestamptz NOT NULL,
	has_narrative_detected boolean NULL,
	has_entities_linked boolean null,
	has_been_processed boolean DEFAULT false NOT NULL,
	CONSTRAINT message_fragment_pk PRIMARY KEY (fragment_id)
);
ALTER TABLE public.document_fragments ADD CONSTRAINT document_fragment_document_fk FOREIGN KEY (document_id) REFERENCES documents(document_id) ON DELETE CASCADE;


CREATE TABLE public.fragment_to_narrative (
	id uuid NOT NULL,
	fragment_id uuid NOT NULL,
	narrative_id uuid NOT NULL,
	confidence float4 NULL,
	created_at timestamptz NOT NULL,
	CONSTRAINT fragment_to_narrative_pk PRIMARY KEY (id),
	CONSTRAINT fragment_to_narrative_narrative_fk FOREIGN KEY (narrative_id) REFERENCES public.narratives(narrative_id) ON DELETE CASCADE,
	CONSTRAINT fragment_to_narrative_document_fragment_fk FOREIGN KEY (fragment_id) REFERENCES public.document_fragments(fragment_id) ON DELETE CASCADE
);

CREATE TABLE public.task_to_telegram_channel (
	id uuid NOT NULL,
	task_id uuid NOT NULL,
	telegram_channel_id uuid NOT NULL,
	created_at timestamptz NOT NULL,
	CONSTRAINT task_to_telegram_channel_pk PRIMARY KEY (id),
	CONSTRAINT task_to_telegram_channel_task_fk FOREIGN KEY (task_id) REFERENCES public.tasks(task_id),
	CONSTRAINT task_to_telegram_channel_telegram_channel_fk FOREIGN KEY (telegram_channel_id) REFERENCES public.telegram_channels(id)
);
ALTER TABLE public.task_to_telegram_channel ADD CONSTRAINT task_to_telegram_channel_unique_pair UNIQUE (task_id,telegram_channel_id);
ALTER TABLE public.task_to_telegram_channel DROP CONSTRAINT task_to_telegram_channel_task_fk;
ALTER TABLE public.task_to_telegram_channel ADD CONSTRAINT task_to_telegram_channel_task_fk FOREIGN KEY (task_id) REFERENCES public.tasks(task_id) ON DELETE CASCADE;

CREATE TABLE public.telegram_channel_to_telegram_channel (
	id uuid NOT NULL,
	referenced_channel_id uuid NOT NULL,
	channel_id uuid NOT NULL,
	message_id uuid NOT NULL,
	reference_type varchar NOT NULL,
	CONSTRAINT telegram_channel_to_telegram_channel_pk PRIMARY KEY (id),
	CONSTRAINT telegram_channel_to_telegram_channel_telegram_channel_fk FOREIGN KEY (referenced_channel_id) REFERENCES public.telegram_channels(id),
	CONSTRAINT telegram_channel_to_telegram_channel_telegram_channel_fk_1 FOREIGN KEY (channel_id) REFERENCES public.telegram_channels(id),
	CONSTRAINT telegram_channel_to_telegram_channel_telegram_message_fk FOREIGN KEY (message_id) REFERENCES public.telegram_messages(id)
);
ALTER TABLE public.telegram_channel_to_telegram_channel ADD CONSTRAINT telegram_channel_to_telegram_channel_unique_four UNIQUE (channel_id,referenced_channel_id,message_id,reference_type);
ALTER TABLE public.telegram_channel_to_telegram_channel ADD created_at timestamptz NOT NULL;
ALTER TABLE public.telegram_channel_to_telegram_channel DROP CONSTRAINT telegram_channel_to_telegram_channel_telegram_message_fk;
ALTER TABLE public.telegram_channel_to_telegram_channel ADD CONSTRAINT telegram_channel_to_telegram_channel_telegram_message_fk FOREIGN KEY (message_id) REFERENCES public.telegram_messages(id) ON DELETE CASCADE;
ALTER TABLE public.telegram_channel_to_telegram_channel DROP CONSTRAINT telegram_channel_to_telegram_channel_telegram_channel_fk_1;
ALTER TABLE public.telegram_channel_to_telegram_channel ADD CONSTRAINT telegram_channel_to_telegram_channel_telegram_channel_fk_1 FOREIGN KEY (channel_id) REFERENCES public.telegram_channels(id) ON DELETE CASCADE;
ALTER TABLE public.telegram_channel_to_telegram_channel DROP CONSTRAINT telegram_channel_to_telegram_channel_telegram_channel_fk;
ALTER TABLE public.telegram_channel_to_telegram_channel ADD CONSTRAINT telegram_channel_to_telegram_channel_telegram_channel_fk FOREIGN KEY (referenced_channel_id) REFERENCES public.telegram_channels(id) ON DELETE CASCADE;

CREATE TABLE public.telegram_external_references (
	id uuid NOT NULL,
	url varchar NOT NULL,
	message_id uuid NOT NULL,
	created_at timestamptz NOT NULL,
	CONSTRAINT external_reference_pk PRIMARY KEY (id),
	CONSTRAINT external_reference_telegram_message_fk FOREIGN KEY (message_id) REFERENCES public.telegram_messages(id) ON DELETE CASCADE
);
ALTER TABLE public.telegram_external_references RENAME COLUMN url TO uri;
ALTER TABLE public.telegram_external_references ADD CONSTRAINT external_reference_unique UNIQUE (uri,message_id);

CREATE TABLE public.resource_tags (
	tag_id uuid NOT NULL,
	tag_name text NOT NULL,
	tag_description text NULL,
	created_at timestamptz NOT NULL,
	CONSTRAINT resource_tag_pk PRIMARY KEY (tag_id)
);

CREATE TABLE public.telegram_channel_to_resource_tag (
	id uuid NOT NULL,
	channel_id uuid NOT NULL,
	tag_id uuid NOT NULL,
	created_at timestamptz NOT NULL,
	CONSTRAINT telegram_channel_to_resource_tag_pk PRIMARY KEY (id),
	CONSTRAINT telegram_channel_to_resource_tag_telegram_channel_fk FOREIGN KEY (channel_id) REFERENCES public.telegram_channels(id) ON DELETE CASCADE,
	CONSTRAINT telegram_channel_to_resource_tag_resource_tag_fk FOREIGN KEY (tag_id) REFERENCES public.resource_tags(tag_id) ON DELETE CASCADE
);


ALTER TABLE public.telegram_message_to_document  ADD CONSTRAINT telegram_message_to_document_document_id_fk FOREIGN KEY (document_id) REFERENCES public.documents(document_id) ON DELETE set NULL;


ALTER TABLE public.tasks ADD is_public boolean DEFAULT false NOT NULL;
ALTER TABLE public.tasks ADD task_name text NULL;



