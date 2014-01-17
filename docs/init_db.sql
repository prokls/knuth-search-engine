-- DB layout

CREATE TABLE documents
(
  id integer NOT NULL DEFAULT nextval('documents_id_seq'::regclass),
  type character varying(20) NOT NULL,
  title character varying(256),
  author character varying(40),
  "timestamp" integer,
  parent integer,
  CONSTRAINT documents_pkey PRIMARY KEY (id)
);

CREATE TABLE metadata
(
  document integer NOT NULL,
  key character varying(40),
  value text
);


-- DB example data

INSERT INTO documents (id, "type", title, author, "timestamp", parent) VALUES (1, 'doc', 'Generative Felgenmodellierung', 'Harald Csaszar',  1180051200, NULL);
INSERT INTO documents (id, "type", title, author, "timestamp", parent) VALUES (2, 'doc', 'Retrospective and Prospective Motion Correction for Magnetic Resonance Imaging of the Head', 'Christian Dold', 1214956800, NULL);
INSERT INTO documents (id, "type", title, author, "timestamp", parent) VALUES (3, 'doc', 'Generative Mesh Modeling', 'Sven Havemann', 1121385600, NULL);
INSERT INTO documents (id, "type", title, author, "timestamp", parent) VALUES (4, 'attach', 'Havemann05generativemesh', 'Sven Havemann', 1123386600, 2);

INSERT INTO metadata (id, document, key, value) VALUES (1, 3, 'institute', 'Institut für ComputerGraphik');
INSERT INTO metadata (id, document, key, value) VALUES (2, 3, 'chapters', '5');




