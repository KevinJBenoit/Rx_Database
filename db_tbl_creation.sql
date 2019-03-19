DROP DATABASE IF EXISTS medication;
CREATE DATABASE medication;
USE medication;


CREATE TABLE drug (
    id INTEGER AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    fda_approval_date DATE,
    total_rx INTEGER NOT NULL
);

CREATE TABLE brand_name (
    id INTEGER AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    drug_id INTEGER NOT NULL,
    FOREIGN KEY(drug_id) REFERENCES drug(id)
);


CREATE TABLE side_effects (
    id INTEGER AUTO_INCREMENT PRIMARY KEY,
    effect VARCHAR(100) UNIQUE NOT NULL,
    drug_id INTEGER NOT NULL,
    brand_id INTEGER NOT NULL,
    FOREIGN KEY(drug_id) REFERENCES drug(id),
    FOREIGN KEY(brand_id) REFERENCES brand_name(id)
);

CREATE TABLE associated_disease (
    id INTEGER AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    drug_id INTEGER NOT NULL,
    brand_id INTEGER NOT NULL,
    FOREIGN KEY(drug_id) REFERENCES drug(id),
    FOREIGN KEY(brand_id) REFERENCES brand_name(id)
);

CREATE TABLE risk_factors (
    id INTEGER AUTO_INCREMENT PRIMARY KEY,
    factor VARCHAR(100) UNIQUE NOT NULL,
    drug_id INTEGER NOT NULL,
    brand_id INTEGER NOT NULL,
    FOREIGN KEY(drug_id) REFERENCES drug(id),
    FOREIGN KEY(brand_id) REFERENCES brand_name(id)
);