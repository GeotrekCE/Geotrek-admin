-- OrderedTrekChild
-------------------
-- parent
-- child
ALTER TABLE trekking_orderedtrekchild ALTER COLUMN "order" SET DEFAULT 0;


-- Practice
-----------
-- name
-- distance
-- cirkwi
-- order
ALTER TABLE trekking_practice ALTER COLUMN color SET DEFAULT '#444444';

-- pictogram


-- RatingScale
--------------
-- practice
-- name
-- order


-- Rating
---------
-- scale
-- name
ALTER TABLE trekking_rating ALTER COLUMN description SET DEFAULT '';
-- order
ALTER TABLE trekking_rating ALTER COLUMN color SET DEFAULT '#ffffff';


-- Trek
-------
-- topo_object
ALTER TABLE trekking_trek ALTER COLUMN departure SET DEFAULT '';
ALTER TABLE trekking_trek ALTER COLUMN arrival SET DEFAULT '';
ALTER TABLE trekking_trek ALTER COLUMN description_teaser SET DEFAULT '';
ALTER TABLE trekking_trek ALTER COLUMN description SET DEFAULT '';
ALTER TABLE trekking_trek ALTER COLUMN ambiance SET DEFAULT '';
ALTER TABLE trekking_trek ALTER COLUMN access SET DEFAULT '';
-- duration
ALTER TABLE trekking_trek ALTER COLUMN advised_parking SET DEFAULT '';
-- parking_location
ALTER TABLE trekking_trek ALTER COLUMN advised_parking SET DEFAULT '';
ALTER TABLE trekking_trek ALTER COLUMN public_transport SET DEFAULT '';
ALTER TABLE trekking_trek ALTER COLUMN advice SET DEFAULT '';
-- ratings
ALTER TABLE trekking_trek ALTER COLUMN ratings_description SET DEFAULT '';
ALTER TABLE trekking_trek ALTER COLUMN gear SET DEFAULT '';
-- themes
-- networks
-- practice
-- accessibilities
ALTER TABLE trekking_trek ALTER COLUMN accessibility_advice SET DEFAULT '';
ALTER TABLE trekking_trek ALTER COLUMN accessibility_covering SET DEFAULT '';
-- accessibility_level
ALTER TABLE trekking_trek ALTER COLUMN accessibility_exposure SET DEFAULT '';
ALTER TABLE trekking_trek ALTER COLUMN accessibility_infrastructure SET DEFAULT '';
ALTER TABLE trekking_trek ALTER COLUMN accessibility_signage SET DEFAULT '';
ALTER TABLE trekking_trek ALTER COLUMN accessibility_slope SET DEFAULT '';
ALTER TABLE trekking_trek ALTER COLUMN accessibility_width SET DEFAULT '';
-- route
-- difficulty
-- web_links
-- information_desks
-- points_reference
-- source
-- portal
-- labels
-- eid
-- eid2
-- pois_excluded
-- reservation_system
ALTER TABLE trekking_trek ALTER COLUMN reservation_id SET DEFAULT '';
-- structure
-- name
ALTER TABLE trekking_trek ALTER COLUMN review SET DEFAULT FALSE;
ALTER TABLE trekking_trek ALTER COLUMN published SET DEFAULT FALSE;
-- publication_date


-- POI
------
-- topo_object
-- pictogram
ALTER TABLE trekking_poi ALTER COLUMN description SET DEFAULT '';
-- type
-- eid
-- structure
--
ALTER TABLE trekking_poi ALTER COLUMN description SET DEFAULT '';
-- name
ALTER TABLE trekking_poi ALTER COLUMN review SET DEFAULT FALSE;
ALTER TABLE trekking_poi ALTER COLUMN published SET DEFAULT FALSE;

-- publication_date


-- ServiceType
--------------
-- practices
-- pictogram
-- name
ALTER TABLE trekking_poi ALTER COLUMN review SET DEFAULT FALSE;
ALTER TABLE trekking_poi ALTER COLUMN published SET DEFAULT FALSE;
-- publication_date


-- Service
----------
-- topo_object
-- type
--eid
--structure
