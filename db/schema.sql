-- =========================================
-- Chinese Checkers Database Schema
-- =========================================

CREATE DATABASE IF NOT EXISTS chinese_checkers;
USE chinese_checkers;

DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS bots_based_players;
DROP TABLE IF EXISTS games;
DROP TABLE IF EXISTS players;

-- =========================================
-- USERS
-- =========================================

CREATE TABLE users (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    name CHAR(30) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    salt VARCHAR(255) NOT NULL,
    score BIGINT UNSIGNED NOT NULL DEFAULT 0,

    PRIMARY KEY (id),
    UNIQUE KEY uq_users_name (name)
) ENGINE=InnoDB;

-- =========================================
-- BOT-BASED PLAYERS
-- =========================================

CREATE TABLE bots_based_players (
    user_id BIGINT UNSIGNED NOT NULL,

    PRIMARY KEY (user_id),

    CONSTRAINT fk_bots_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
) ENGINE=InnoDB;

-- =========================================
-- GAMES
-- =========================================

CREATE TABLE games (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    external_id BIGINT UNSIGNED NOT NULL,
    player_count TINYINT UNSIGNED NOT NULL,
    elapsed BIGINT UNSIGNED NOT NULL DEFAULT 0,
    timestamp_end BIGINT UNSIGNED NULL,
    time_limit BIGINT UNSIGNED NOT NULL DEFAULT 0,
    increment_value BIGINT UNSIGNED NOT NULL DEFAULT 0,
    casual BOOLEAN NOT NULL DEFAULT FALSE,
    ranked BOOLEAN NOT NULL DEFAULT FALSE,

    PRIMARY KEY (id),
    UNIQUE KEY uq_games_external_id (external_id)
) ENGINE=InnoDB;

-- =========================================
-- PLAYERS
-- =========================================

CREATE TABLE players (
    game_id BIGINT UNSIGNED NOT NULL,
    user_id BIGINT UNSIGNED NOT NULL,
    player_number TINYINT UNSIGNED NOT NULL,
    player_rank TINYINT UNSIGNED NULL,
    score_change BIGINT NOT NULL DEFAULT 0,
    timed_out BOOLEAN NOT NULL DEFAULT FALSE,

    PRIMARY KEY (game_id, user_id),

    CONSTRAINT fk_players_game
        FOREIGN KEY (game_id)
        REFERENCES games(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_players_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
) ENGINE=InnoDB;
