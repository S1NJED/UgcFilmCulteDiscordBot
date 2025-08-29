BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "movies" (
	"cinema_id"	TEXT,
	"title"	TEXT
);
CREATE TABLE IF NOT EXISTS "cinemas" (
	"id"	INTEGER,
	"name"	TEXT,
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "notify_channel" (
	"id"	INTEGER DEFAULT 1,
	"message"	TEXT,
	"channel_id"	INTEGER
);
INSERT INTO "notify_channel" VALUES (1,NULL,NULL);
COMMIT;
