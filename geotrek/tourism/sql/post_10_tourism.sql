ALTER TABLE tourism_touristiccontent ALTER COLUMN uuid SET DEFAULT gen_random_uuid();
ALTER TABLE tourism_touristicevent ALTER COLUMN uuid SET DEFAULT gen_random_uuid();