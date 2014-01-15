-- DB layout

CREATE TABLE IF NOT EXISTS documents (
    `id` INT PRIMARY KEY AUTO_INCREMENT,
    `type` CHAR(20) NOT NULL,
    `title` VARCHAR(120) DEFAULT NULL,
    `author` VARCHAR(40) DEFAULT NULL,
    `timestamp` INT,
    `parent` INT
);

CREATE TABLE IF NOT EXISTS metadata (
    `document` INT NOT NULL,
    `key` VARCHAR(40),
    `value` TEXT
);

-- DB example data

INSERT INTO documents VALUES (1, "doc", "Generative Felgenmodellierung", "Harald Csaszar",  1180051200, NULL);
INSERT INTO documents VALUES (2, "doc", "Retrospective and Prospective Motion Correction for Magnetic Resonance Imaging of the Head", "Christian Dold", 1214956800, NULL);
INSERT INTO documents VALUES (3, "doc", "Generative Mesh Modeling", "Sven Havemann", 1121385600, NULL);
INSERT INTO documents VALUES (4, "attach", "Havemann05generativemesh", "Sven Havemann", 1123386600, 2);

INSERT INTO metadata VALUES (3, "institute", "Institut für ComputerGraphik");
INSERT INTO metadata VALUES (3, "chapters", "5");







CREATE TABLE documents
(
  id integer NOT NULL,
  "type" character varying(20) NOT NULL,
  title character varying(256),
  author character varying(40),
  "timestamp" integer,
  parent integer,
  CONSTRAINT documents_pkey PRIMARY KEY (id)
);

CREATE SEQUENCE documents_id_seq;
ALTER TABLE documents ALTER id SET DEFAULT NEXTVAL('documents_id_seq');

CREATE TABLE metadata
(
  document integer NOT NULL,
  key character varying(40),
  value text
);

INSERT INTO documents (id, "type", title, author, "timestamp", parent) VALUES (1, 'doc', 'Generative Felgenmodellierung', 'Harald Csaszar',  1180051200, NULL);
INSERT INTO documents (id, "type", title, author, "timestamp", parent) VALUES (2, 'doc', 'Retrospective and Prospective Motion Correction for Magnetic Resonance Imaging of the Head', 'Christian Dold', 1214956800, NULL);
INSERT INTO documents (id, "type", title, author, "timestamp", parent) VALUES (3, 'doc', 'Generative Mesh Modeling', 'Sven Havemann', 1121385600, NULL);
INSERT INTO documents (id, "type", title, author, "timestamp", parent) VALUES (4, 'attach', 'Havemann05generativemesh', 'Sven Havemann', 1123386600, 2);

INSERT INTO metadata (id, document, key, value) VALUES (1, 3, 'institute', 'Institut für ComputerGraphik');
INSERT INTO metadata (id, document, key, value) VALUES (2, 3, 'chapters', '5');


CREATE TABLE documents
(
  id integer NOT NULL DEFAULT nextval('documents_id_seq'::regclass),
  type character varying(20) NOT NULL,
  title character varying(256),
  author character varying(40),
  "timestamp" integer,
  parent integer,
  CONSTRAINT documents_pkey PRIMARY KEY (id)
)

