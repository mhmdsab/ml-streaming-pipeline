DROP DATABASE IF EXISTS fashion_db;    

CREATE DATABASE fashion_db;    

\c fashion_db;        

CREATE TABLE IF NOT EXISTS fashion (
  p_id SERIAL NOT NULL,
  fashion_id INT ,
  fashion_type varchar(250) ,
  broker_type varchar(250),
  PRIMARY KEY (p_id)
);
