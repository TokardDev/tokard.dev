DROP TABLE IF EXISTS redirects;

CREATE TABLE redirects (
  code TEXT PRIMARY KEY,
  link TEXT NOT NULL
);