-- -------------------------------
-- Project
-- -------------------------------
BEGIN
	EXECUTE IMMEDIATE 'DROP TABLE project';
EXCEPTION
	WHEN OTHERS THEN
		IF SQLCODE != -942 THEN
			RAISE;
		END IF;
END;
/
CREATE TABLE project(
	id number(10) PRIMARY KEY,
	name varchar2(255),
	CONSTRAINT project_name UNIQUE (name));

BEGIN
  EXECUTE IMMEDIATE 'DROP SEQUENCE project_seq';
EXCEPTION
  WHEN OTHERS THEN
    IF SQLCODE != -2289 THEN
      RAISE;
    END IF;
END;
/
CREATE SEQUENCE project_seq START WITH 1 INCREMENT BY 1;
CREATE OR REPLACE TRIGGER project_seq_tr
	BEFORE INSERT ON project FOR EACH ROW
	WHEN (new.id IS NULL)
BEGIN
	SELECT project_seq.NEXTVAL INTO :new.id FROM DUAL;
END;
/


-- -------------------------------
-- Users
-- -------------------------------
BEGIN
	EXECUTE IMMEDIATE 'DROP TABLE users';
EXCEPTION
	WHEN OTHERS THEN
		IF SQLCODE != -942 THEN
			RAISE;
		END IF;
END;
/
CREATE TABLE users (
	id number(10) PRIMARY KEY,
	name varchar2(256),
	email varchar2(256),
	CONSTRAINT users_name UNIQUE (name, email));

BEGIN
  EXECUTE IMMEDIATE 'DROP SEQUENCE users_seq';
EXCEPTION
  WHEN OTHERS THEN
    IF SQLCODE != -2289 THEN
      RAISE;
    END IF;
END;
/
CREATE SEQUENCE users_seq START WITH 1 INCREMENT BY 1;
CREATE OR REPLACE TRIGGER users_seq_tr
 BEFORE INSERT ON users FOR EACH ROW
 WHEN (new.id IS NULL)
BEGIN
 SELECT users_seq.NEXTVAL INTO :new.id FROM DUAL;
END;
/


-- -------------------------------
-- Repository
-- -------------------------------
BEGIN
	EXECUTE IMMEDIATE 'DROP TABLE repository';
EXCEPTION
	WHEN OTHERS THEN
		IF SQLCODE != -942 THEN
			RAISE;
		END IF;
END;
/
CREATE TABLE repository(
	id number(10) PRIMARY KEY,
	project_id number(10),
	name varchar2(255),
	CONSTRAINT repository_name UNIQUE (name));

BEGIN
  EXECUTE IMMEDIATE 'DROP SEQUENCE repository_seq';
EXCEPTION
  WHEN OTHERS THEN
    IF SQLCODE != -2289 THEN
      RAISE;
    END IF;
END;
/
CREATE SEQUENCE repository_seq START WITH 1 INCREMENT BY 1;
CREATE OR REPLACE TRIGGER repository_seq_tr
 BEFORE INSERT ON repository FOR EACH ROW
 WHEN (new.id IS NULL)
BEGIN
 SELECT repository_seq.NEXTVAL INTO :new.id FROM DUAL;
END;
/


-- -------------------------------
-- Reference
-- -------------------------------
BEGIN
	EXECUTE IMMEDIATE 'DROP TABLE reference';
EXCEPTION
	WHEN OTHERS THEN
		IF SQLCODE != -942 THEN
			RAISE;
		END IF;
END;
/
CREATE TABLE reference(
	id number(10) PRIMARY KEY,
	repo_id number(10),
	name varchar2(255),
	type varchar2(255),
	CONSTRAINT reference_name UNIQUE (repo_id, name, type));

BEGIN
  EXECUTE IMMEDIATE 'DROP SEQUENCE reference_seq';
EXCEPTION
  WHEN OTHERS THEN
    IF SQLCODE != -2289 THEN
      RAISE;
    END IF;
END;
/
CREATE SEQUENCE reference_seq START WITH 1 INCREMENT BY 1;
CREATE OR REPLACE TRIGGER reference_seq_tr
 BEFORE INSERT ON reference FOR EACH ROW
 WHEN (new.id IS NULL)
BEGIN
 SELECT reference_seq.NEXTVAL INTO :new.id FROM DUAL;
END;
/


-- -------------------------------
-- Commits
-- -------------------------------
BEGIN
	EXECUTE IMMEDIATE 'DROP TABLE commits';
EXCEPTION
	WHEN OTHERS THEN
		IF SQLCODE != -942 THEN
			RAISE;
		END IF;
END;
/
CREATE TABLE commits(
	id number(10) PRIMARY KEY,
	repo_id number(10),
	sha varchar2(512),
	message varchar2(512),
	author_id number(10),
	committer_id number(10),
	authored_date timestamp(0) DEFAULT NULL,
	committed_date timestamp(0) DEFAULT NULL,
	commit_size number(10),
	CONSTRAINT s UNIQUE (sha, repo_id));

BEGIN
  EXECUTE IMMEDIATE 'DROP SEQUENCE commits_seq';
EXCEPTION
  WHEN OTHERS THEN
    IF SQLCODE != -2289 THEN
      RAISE;
    END IF;
END;
/
CREATE SEQUENCE commits_seq START WITH 1 INCREMENT BY 1;
CREATE OR REPLACE TRIGGER commits_seq_tr
 BEFORE INSERT ON commits FOR EACH ROW
 WHEN (new.id IS NULL)
BEGIN
 SELECT commits_seq.NEXTVAL INTO :new.id FROM DUAL;
END;
/
CREATE INDEX sha ON commits (sha);
CREATE INDEX auth ON commits (author_id);
CREATE INDEX comm ON commits (committer_id);


-- -------------------------------
-- Commit_parent
-- -------------------------------
BEGIN
	EXECUTE IMMEDIATE 'DROP TABLE commit_parent';
EXCEPTION
	WHEN OTHERS THEN
		IF SQLCODE != -942 THEN
			RAISE;
		END IF;
END;
/
CREATE TABLE commit_parent(
	repo_id number(10),
	commit_id number(10),
	commit_sha varchar2(512),
	parent_id number(10),
	parent_sha varchar2(512),
	CONSTRAINT copa PRIMARY KEY (repo_id, commit_id, parent_id),
	CONSTRAINT cshapsha UNIQUE (repo_id, commit_id, parent_sha));


-- -------------------------------
-- Commit_in_reference
-- -------------------------------
BEGIN
	EXECUTE IMMEDIATE 'DROP TABLE commit_in_reference';
EXCEPTION
	WHEN OTHERS THEN
		IF SQLCODE != -942 THEN
			RAISE;
		END IF;
END;
/
CREATE TABLE commit_in_reference(
	repo_id number(10),
	commit_id number(10),
	ref_id number(10),
	CONSTRAINT core PRIMARY KEY (commit_id, ref_id));


-- -------------------------------
-- Files
-- -------------------------------
BEGIN
	EXECUTE IMMEDIATE 'DROP TABLE files';
EXCEPTION
	WHEN OTHERS THEN
		IF SQLCODE != -942 THEN
			RAISE;
		END IF;
END;
/
CREATE TABLE files(
	id number(10) PRIMARY KEY,
	repo_id number(10),
	name varchar2(512),
	ext varchar2(255),
	CONSTRAINT rerena UNIQUE (repo_id, name));

BEGIN
  EXECUTE IMMEDIATE 'DROP SEQUENCE files_seq';
EXCEPTION
  WHEN OTHERS THEN
    IF SQLCODE != -2289 THEN
      RAISE;
    END IF;
END;
/
CREATE SEQUENCE files_seq START WITH 1 INCREMENT BY 1;
CREATE OR REPLACE TRIGGER files_seq_tr
 BEFORE INSERT ON files FOR EACH ROW
 WHEN (new.id IS NULL)
BEGIN
 SELECT files_seq.NEXTVAL INTO :new.id FROM DUAL;
END;
/


-- -------------------------------
-- File_renamed
-- -------------------------------
BEGIN
	EXECUTE IMMEDIATE 'DROP TABLE file_renamed';
EXCEPTION
	WHEN OTHERS THEN
		IF SQLCODE != -942 THEN
			RAISE;
		END IF;
END;
/
CREATE TABLE file_renamed (
	repo_id number(10),
	current_file_id number(10),
	previous_file_id number(10),
	CONSTRAINT cpc PRIMARY KEY (current_file_id, previous_file_id));


-- -------------------------------
-- File_modification
-- -------------------------------
BEGIN
	EXECUTE IMMEDIATE 'DROP TABLE file_modification';
EXCEPTION
	WHEN OTHERS THEN
		IF SQLCODE != -942 THEN
			RAISE;
		END IF;
END;
/
CREATE TABLE file_modification (
	id number(10) PRIMARY KEY,
	commit_id number(10),
	file_id number(10),
	status varchar2(10),
	additions number(10),
	deletions number(10),
	changes number(10),
	patch blob,
	CONSTRAINT cf UNIQUE (commit_id, file_id));

BEGIN
  EXECUTE IMMEDIATE 'DROP SEQUENCE file_modification_seq';
EXCEPTION
  WHEN OTHERS THEN
    IF SQLCODE != -2289 THEN
      RAISE;
    END IF;
END;
/
CREATE SEQUENCE file_modification_seq START WITH 1 INCREMENT BY 1;
CREATE OR REPLACE TRIGGER file_modification_seq_tr
 BEFORE INSERT ON file_modification FOR EACH ROW
 WHEN (new.id IS NULL)
BEGIN
 SELECT file_modification_seq.NEXTVAL INTO :new.id FROM DUAL;
END;
/


-- -------------------------------
-- Line_detail
-- -------------------------------
BEGIN
	EXECUTE IMMEDIATE 'DROP TABLE line_detail';
EXCEPTION
	WHEN OTHERS THEN
		IF SQLCODE != -942 THEN
			RAISE;
		END IF;
END;
/
CREATE TABLE line_detail(
	file_modification_id number(10),
	type varchar2(25),
	line_number number(20),
	is_commented number(1),
	is_partially_commented number(1),
	is_empty number(1),
	content blob,
	CONSTRAINT fityli PRIMARY KEY (file_modification_id, type, line_number));
