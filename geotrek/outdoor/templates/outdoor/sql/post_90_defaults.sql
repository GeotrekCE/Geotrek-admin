-- Sector
---------
-- name


-- Sector
---------
-- name


-- Sector
---------
-- name
ALTER TABLE outdoor_sector ALTER COLUMN date_insert SET DEFAULT now();
ALTER TABLE outdoor_sector ALTER COLUMN date_update SET DEFAULT now();

-- Practice
-----------
-- name
-- sector
-- pictogram
ALTER TABLE outdoor_practice ALTER COLUMN date_insert SET DEFAULT now();
ALTER TABLE outdoor_practice ALTER COLUMN date_update SET DEFAULT now();


-- RatingScale
--------------
-- practice
-- name
-- order


-- Rating
---------
-- scale
-- name
ALTER TABLE outdoor_rating ALTER COLUMN description SET DEFAULT '';
-- order
ALTER TABLE outdoor_rating ALTER COLUMN color SET DEFAULT '#ffffff';


-- SiteType
-----------
-- name
-- practice
ALTER TABLE outdoor_sitetype ALTER COLUMN date_insert SET DEFAULT now();
ALTER TABLE outdoor_sitetype ALTER COLUMN date_update SET DEFAULT now();

-- CourseType
-------------
-- name
-- practice
ALTER TABLE outdoor_coursetype ALTER COLUMN date_insert SET DEFAULT now();
ALTER TABLE outdoor_coursetype ALTER COLUMN date_update SET DEFAULT now();

-- Site
-------
-- geom
-- parent
-- practice
ALTER TABLE outdoor_site ALTER COLUMN description SET DEFAULT '';
ALTER TABLE outdoor_site ALTER COLUMN description_teaser SET DEFAULT '';
ALTER TABLE outdoor_site ALTER COLUMN ambiance SET DEFAULT '';
ALTER TABLE outdoor_site ALTER COLUMN advice SET DEFAULT '';
-- ratings
ALTER TABLE outdoor_site ALTER COLUMN period SET DEFAULT '';
ALTER TABLE outdoor_site ALTER COLUMN orientation SET DEFAULT '[]'::JSON;
ALTER TABLE outdoor_site ALTER COLUMN wind SET DEFAULT '[]'::JSON;
-- labels
-- themes
-- information_desks
-- portal
-- source
-- pois_excluded
-- weblinks
ALTER TABLE outdoor_site ALTER COLUMN accessibility SET DEFAULT '';
-- type
-- eid
-- managers
ALTER TABLE outdoor_site ALTER COLUMN uuid SET DEFAULT gen_random_uuid();
ALTER TABLE outdoor_site ALTER COLUMN provider SET DEFAULT '';

-- OrderedCourseChild
---------------------
-- parent
-- child
ALTER TABLE outdoor_orderedcoursechild ALTER COLUMN "order" SET DEFAULT 0;


-- Course
---------
-- geom
-- parent_sites
ALTER TABLE outdoor_course ALTER COLUMN description SET DEFAULT '';
ALTER TABLE outdoor_course ALTER COLUMN ratings_description SET DEFAULT '';
ALTER TABLE outdoor_course ALTER COLUMN gear SET DEFAULT '';
-- duration
ALTER TABLE outdoor_course ALTER COLUMN advice SET DEFAULT '';
ALTER TABLE outdoor_course ALTER COLUMN accessibility SET DEFAULT '';
ALTER TABLE outdoor_course ALTER COLUMN equipment SET DEFAULT '';
-- ratings
-- height
-- eid
-- type
-- pois_excluded
-- points_reference
ALTER TABLE outdoor_course ALTER COLUMN uuid SET DEFAULT gen_random_uuid();
ALTER TABLE outdoor_course ALTER COLUMN published SET DEFAULT FALSE;
-- publication_date
-- name
ALTER TABLE outdoor_course ALTER COLUMN review SET DEFAULT FALSE;
-- structure
-- geom_3d
ALTER TABLE outdoor_course ALTER COLUMN "length" SET DEFAULT 0.0;
ALTER TABLE outdoor_course ALTER COLUMN ascent SET DEFAULT 0.0;
ALTER TABLE outdoor_course ALTER COLUMN descent SET DEFAULT 0;
ALTER TABLE outdoor_course ALTER COLUMN min_elevation SET DEFAULT 0;
ALTER TABLE outdoor_course ALTER COLUMN max_elevation SET DEFAULT 0;
ALTER TABLE outdoor_course ALTER COLUMN slope SET DEFAULT 0.0;
ALTER TABLE outdoor_course ALTER COLUMN date_insert SET DEFAULT now();
ALTER TABLE outdoor_course ALTER COLUMN date_update SET DEFAULT now();
ALTER TABLE outdoor_course ALTER COLUMN provider SET DEFAULT '';
