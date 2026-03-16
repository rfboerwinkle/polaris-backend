USE chinese_checkers;

SET FOREIGN_KEY_CHECKS = 0;

TRUNCATE players;
TRUNCATE games;
TRUNCATE users;
TRUNCATE bots_based_players;

SET FOREIGN_KEY_CHECKS = 1;
-- =========================================
-- USERS
-- =========================================

INSERT INTO users (name, password_hash, salt, score) VALUES
('jhustin', 'hash1', 'salt1', 1200),
('bhen', 'hash2', 'salt2', 1100),
('boris', 'hash3', 'salt3', 1050),
('bot_easy', 'hash_bot', 'salt_bot', 1000);

-- =========================================
-- BOT USERS
-- =========================================

INSERT INTO bots_based_players (user_id)
VALUES (4);

-- =========================================
-- GAMES
-- =========================================

INSERT INTO games (
    external_id,
    player_count,
    elapsed,
    timestamp_end,
    time_limit,
    increment_value,
    casual,
    ranked
) VALUES
(1001, 2, 600, UNIX_TIMESTAMP(), 300, 5, TRUE, FALSE),
(1002, 3, 900, UNIX_TIMESTAMP(), 300, 5, FALSE, TRUE);

-- =========================================
-- PLAYERS IN GAME 1 (jhustin vs bot)
-- =========================================

INSERT INTO players (
    game_id,
    user_id,
    player_number,
    player_rank,
    score_change,
    timed_out
) VALUES
(1, 1, 1, 1, 0, FALSE),
(1, 4, 2, 2, 0, FALSE);

-- =========================================
-- PLAYERS IN GAME 2 (jhustin, bhen, boris)
-- =========================================

INSERT INTO players (
    game_id,
    user_id,
    player_number,
    player_rank,
    score_change,
    timed_out
) VALUES
(2, 1, 1, 2, 0, FALSE),
(2, 2, 2, 1, 10, FALSE),
(2, 3, 3, 3, -10, FALSE);
