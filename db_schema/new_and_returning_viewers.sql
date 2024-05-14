-- New and returning viewers table
CREATE TABLE IF NOT EXISTS New_and_returning_viewers (
    "Date" TIMESTAMP,
    "New and returning viewers" TEXT,
    "Views" INTEGER,
    PRIMARY KEY ("Date", "New and returning viewers")
);
