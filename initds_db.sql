CREATE DATABASE IF NOT EXISTS prode;
use prode;


CREATE TABLE IF NOT EXISTS usuarios (
    id INT PRIMARY KEY,
    nombre VARCHAR(50),
    mail VARCHAR(50)
);
