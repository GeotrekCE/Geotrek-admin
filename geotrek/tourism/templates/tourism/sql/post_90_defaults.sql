-- InformationDeskType
----------------------
-- label
-- pictogram


-- LabelAccessibility
---------------------
-- label
-- pictogram


-- InformationDesk
------------------
-- name
-- type
ALTER TABLE tourism_informationdesk ALTER COLUMN description SET DEFAULT '';
-- phone
-- email
-- website
-- photo
-- street
-- postal_code
-- municipality
ALTER TABLE tourism_informationdesk ALTER COLUMN accessibility SET DEFAULT '';
-- label_accessibility
-- geom
-- eid
ALTER TABLE tourism_informationdesk ALTER COLUMN uuid SET DEFAULT gen_random_uuid();
ALTER TABLE tourism_informationdesk ALTER COLUMN provider SET DEFAULT '';


-- TouristicContentCategory
---------------------------
-- label
ALTER TABLE tourism_touristiccontentcategory ALTER COLUMN geometry_type SET DEFAULT 'point';
ALTER TABLE tourism_touristiccontentcategory ALTER COLUMN type1_label SET DEFAULT '';
ALTER TABLE tourism_touristiccontentcategory ALTER COLUMN type2_label SET DEFAULT '';
-- order
ALTER TABLE tourism_touristiccontentcategory ALTER COLUMN color SET DEFAULT '#444444';
-- pictogram


-- TouristicContentType
-----------------------
-- label
-- category
-- in_list
-- pictogram


-- TouristicContent
-------------------
ALTER TABLE tourism_touristiccontent ALTER COLUMN description_teaser SET DEFAULT '';
ALTER TABLE tourism_touristiccontent ALTER COLUMN description SET DEFAULT '';
-- themes
-- geom
-- category
ALTER TABLE tourism_touristiccontent ALTER COLUMN contact SET DEFAULT '';
-- email
-- website
ALTER TABLE tourism_touristiccontent ALTER COLUMN practical_info SET DEFAULT '';
-- type1
-- type2
-- source
-- portal
ALTER TABLE tourism_touristiccontent ALTER COLUMN accessibility SET DEFAULT '';
-- label_accessibility
-- eid
-- reservation_system
ALTER TABLE tourism_touristiccontent ALTER COLUMN reservation_id SET DEFAULT '';
ALTER TABLE tourism_touristiccontent ALTER COLUMN approved SET DEFAULT FALSE;
ALTER TABLE tourism_touristiccontent ALTER COLUMN uuid SET DEFAULT gen_random_uuid();
-- name
ALTER TABLE tourism_touristiccontent ALTER COLUMN review SET DEFAULT FALSE;
ALTER TABLE tourism_touristiccontent ALTER COLUMN published SET DEFAULT FALSE;
-- publication_date
-- structure
ALTER TABLE tourism_touristiccontent ALTER COLUMN date_insert SET DEFAULT now();
ALTER TABLE tourism_touristiccontent ALTER COLUMN date_update SET DEFAULT now();
ALTER TABLE tourism_touristiccontent ALTER COLUMN provider SET DEFAULT '';
-- deleted


-- TouristicEventType
---------------------
-- type
-- pictogram


-- TouristicEvent
-----------------
ALTER TABLE tourism_touristicevent ALTER COLUMN description_teaser SET DEFAULT '';
ALTER TABLE tourism_touristicevent ALTER COLUMN description SET DEFAULT '';
-- themes
-- geom
-- begin_date
-- end_date
ALTER TABLE tourism_touristicevent ALTER COLUMN duration SET DEFAULT '';
ALTER TABLE tourism_touristicevent ALTER COLUMN meeting_point SET DEFAULT '';
-- start_time
-- end_time
ALTER TABLE tourism_touristicevent ALTER COLUMN contact SET DEFAULT '';
-- email
-- website
ALTER TABLE tourism_touristicevent ALTER COLUMN organizer SET DEFAULT '';
ALTER TABLE tourism_touristicevent ALTER COLUMN speaker SET DEFAULT '';
-- type
ALTER TABLE tourism_touristicevent ALTER COLUMN accessibility SET DEFAULT '';
ALTER TABLE tourism_touristicevent ALTER COLUMN participant_number SET DEFAULT '';
ALTER TABLE tourism_touristicevent ALTER COLUMN booking SET DEFAULT '';
-- target_audience
ALTER TABLE tourism_touristicevent ALTER COLUMN practical_info SET DEFAULT '';
-- source
-- portal
-- eid
ALTER TABLE tourism_touristicevent ALTER COLUMN approved SET DEFAULT FALSE;
ALTER TABLE tourism_touristicevent ALTER COLUMN uuid SET DEFAULT gen_random_uuid();
-- name
ALTER TABLE tourism_touristicevent ALTER COLUMN review SET DEFAULT FALSE;
ALTER TABLE tourism_touristicevent ALTER COLUMN published SET DEFAULT FALSE;
-- publication_date
-- structure
ALTER TABLE tourism_touristiccontent ALTER COLUMN date_insert SET DEFAULT now();
ALTER TABLE tourism_touristiccontent ALTER COLUMN date_update SET DEFAULT now();
-- deleted
ALTER TABLE tourism_touristicevent ALTER COLUMN provider SET DEFAULT '';
