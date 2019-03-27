DROP DATABASE IF EXISTS medication;
CREATE DATABASE medication;
USE medication;


CREATE TABLE drugs (
    id INTEGER AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    total_rx INTEGER NOT NULL
);

CREATE TABLE brand_names (
    id INTEGER AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    drug_id INTEGER NOT NULL,
    FOREIGN KEY(drug_id) REFERENCES drugs(id)
);


CREATE TABLE side_effects (
    id INTEGER AUTO_INCREMENT PRIMARY KEY,
    effect VARCHAR(100) UNIQUE NOT NULL,
    drug_id INTEGER NOT NULL,
    FOREIGN KEY(drug_id) REFERENCES drugs(id)
);

CREATE TABLE associated_diseases (
    id INTEGER AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL
);


CREATE TABLE treats (
    disease_id INTEGER NOT NULL,
    drug_id INTEGER NOT NULL,
    FOREIGN KEY(disease_id) REFERENCES associated_diseases(id),
    FOREIGN KEY(drug_id) REFERENCES drugs(id),
    PRIMARY KEY(disease_id, drug_id)
);