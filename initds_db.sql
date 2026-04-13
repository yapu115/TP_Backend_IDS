CREATE DATABASE IF NOT EXISTS prode;
use prode;


CREATE TABLE usuarios(
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NULL,
    email VARCHAR(50) NULL
);
CREATE TABLE partidos(
    id INT NOT NULL,
    equipo_local VARCHAR(50) NULL,
    equipo_visitante VARCHAR(50) NULL,
    fecha DATE NULL,
    estadio VARCHAR(50) NULL,
    ciudad VARCHAR(50) NULL,
    fase ENUM(
        'grupos',
        'dieciseisavos',
        'octavos',
        'cuartos',
        'semis',
        'final'
    ) NULL,
    PRIMARY KEY(id)
);
CREATE TABLE resultados(
    id INT NOT NULL,
    goles_local INT NULL,
    goles_visitante INT NULL,
    jugado BOOLEAN NULL,
    PRIMARY KEY(id),
    FOREIGN KEY(id) REFERENCES partidos(id)
);
CREATE TABLE predicciones(
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NULL,
    partido_id INT NULL,
    goles_local INT NULL,
    goles_visitante INT NULL,
    UNIQUE(usuario_id, partido_id),
    FOREIGN KEY(partido_id) REFERENCES partidos(id),
    FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
);