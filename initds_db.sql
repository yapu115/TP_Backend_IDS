CREATE DATABASE IF NOT EXISTS prode;
use prode;


CREATE TABLE IF NOT EXISTS usuarios(
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NULL,
    email VARCHAR(50) NULL
);
CREATE TABLE IF NOT EXISTS partidos(
    id INT NOT NULL AUTO_INCREMENT,
    equipo_local VARCHAR(50) NOT NULL,
    equipo_visitante VARCHAR(50) NOT NULL,
    fecha DATE NOT NULL,
    estadio VARCHAR(50) NULL,
    ciudad VARCHAR(50) NULL,
    fase ENUM(
        'grupos',
        'dieciseisavos',
        'octavos',
        'cuartos',
        'semis',
        'final'
    ) NOT NULL,
    PRIMARY KEY(id)
);
CREATE TABLE IF NOT EXISTS resultados(
    id INT NOT NULL,
    goles_local INT NULL,
    goles_visitante INT NULL,
    jugado BOOLEAN NULL,
    PRIMARY KEY(id),
    FOREIGN KEY(id) REFERENCES partidos(id)
);
CREATE TABLE IF NOT EXISTS predicciones(
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NULL,
    partido_id INT NULL,
    goles_local INT NULL,
    goles_visitante INT NULL,
    UNIQUE(usuario_id, partido_id),
    FOREIGN KEY(partido_id) REFERENCES partidos(id),
    FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
);

INSERT IGNORE INTO usuarios (id, nombre, email) VALUES 
(1, 'Administrador', 'admin@prode.com'),
(2, 'Juan Perez', 'juan@ejemplo.com');

INSERT IGNORE INTO partidos (id, equipo_local, equipo_visitante, fecha, estadio, ciudad, fase) VALUES 
(1, 'Argentina', 'Brasil', '2026-05-19', 'Monumental', 'Buenos Aires', 'grupos'),
(2, 'Francia', 'Brasil', '2026-05-19', 'Monumental', 'Buenos Aires', 'grupos'),
(3, 'Brasil', 'Argentina', '2026-06-15', 'Estadio Lusail', 'Lusail', 'grupos'),
(4, 'Alemania', 'España', '2026-06-15', 'Estadio AlBayt', 'Al Khor', 'grupos'),
(5, 'Argentina', 'Alemania', '2026-06-24', 'Estadio Maracaná', 'Rio de Janeiro', 'cuartos');

INSERT IGNORE INTO resultados (id, goles_local, goles_visitante, jugado) VALUES 
(1, 2, 1, TRUE),
(2, 1, 0, TRUE),
(3, 0, 1, TRUE),
(4, 1, 1, TRUE),
(5, NULL, NULL, FALSE);