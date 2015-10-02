-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.
DROP VIEW records;
DROP TABLE matches;
DROP TABLE players;

CREATE TABLE players (
    id SERIAL, -- auto incremented player id
    name TEXT NOT NULL,
    PRIMARY KEY (id)
);

-- 'matches' table has all information about matches
-- A row has created when a match was reported.
CREATE TABLE matches (
    id SERIAL, -- auto incremented match id
    winner INT REFERENCES players(id), -- foreign key
    loser INT REFERENCES players(id), -- foreign key
    draw BOOLEAN NOT NULL DEFAULT FALSE, -- if match is tied, set TRUE
    PRIMARY KEY (id)
);

-- View 'records' generates new virtual table and contains each player's wins count and match count
CREATE VIEW records AS
    SELECT players.id, players.name, count(matches.winner) AS wins,
    (SELECT count(*) FROM matches WHERE players.id = matches.winner OR players.id = matches.loser) AS matches
    FROM players LEFT JOIN matches ON players.id = matches.winner AND matches.draw = false
    GROUP BY players.id
    ;
