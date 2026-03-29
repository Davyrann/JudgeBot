CREATE TABLE IF NOT EXISTS warns (
    id INTEGER NOT NULL,
    user_id BIGINT NOT NULL,
    server_id BIGINT NOT NULL,
    moderator_id BIGINT NOT NULL,
    reason VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, server_id, id)
);

CREATE TABLE IF NOT EXISTS team_member (
    id SERIAL PRIMARY KEY,
    nama TEXT NOT NULL,
    rank TEXT NOT NULL,
    jabatan TEXT NOT NULL,
    user_id BIGINT NOT NULL DEFAULT 0
);

create table IF NOT EXISTS bounty
(
    bounty_id integer generated always as identity
        constraint bounty_pk
            primary key,
    user_id   bigint,
    target    text,
    reason    text,
    payout    bigint
);
create table IF NOT EXISTS blacklisted_bounty
(
    user_id     bigint                not null
        constraint blacklisted_bounty_pk
            primary key,
    blacklisted boolean default false not null
);
