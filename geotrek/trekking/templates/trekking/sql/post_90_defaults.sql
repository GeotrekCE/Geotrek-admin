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
ALTER TABLE trekking_practice ALTER COLUMN date_insert SET DEFAULT now();
ALTER TABLE trekking_practice ALTER COLUMN date_update SET DEFAULT now();
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
ALTER TABLE trekking_trek ALTER COLUMN provider SET DEFAULT '';
-- route
-- difficulty
-- web_links
-- related_treks
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


-- TrekRelationship
-------------------
ALTER TABLE trekking_trekrelationship ALTER COLUMN has_common_departure SET DEFAULT FALSE;
ALTER TABLE trekking_trekrelationship ALTER COLUMN has_common_edge SET DEFAULT FALSE;
ALTER TABLE trekking_trekrelationship ALTER COLUMN is_circuit_step SET DEFAULT FALSE;
-- trek_a
-- trek_b

-- TrekNetwork
--------------
-- network
-- pictogram
ALTER TABLE trekking_treknetwork ALTER COLUMN date_insert SET DEFAULT now();
ALTER TABLE trekking_treknetwork ALTER COLUMN date_update SET DEFAULT now();

-- Accessibility
----------------
-- name
-- cirkwi
-- pictogram
ALTER TABLE trekking_accessibility ALTER COLUMN date_insert SET DEFAULT now();
ALTER TABLE trekking_accessibility ALTER COLUMN date_update SET DEFAULT now();

-- AccessibilityLevel
---------------------
-- name
ALTER TABLE trekking_accessibilitylevel ALTER COLUMN date_insert SET DEFAULT now();
ALTER TABLE trekking_accessibilitylevel ALTER COLUMN date_update SET DEFAULT now();

-- Route
--------
-- name
-- pictogram
ALTER TABLE trekking_route ALTER COLUMN date_insert SET DEFAULT now();
ALTER TABLE trekking_route ALTER COLUMN date_update SET DEFAULT now();

-- DifficultyLevel
------------------
-- difficulty
-- cirkwi_level
-- cirkwi
-- pictogram
ALTER TABLE trekking_difficultylevel ALTER COLUMN date_insert SET DEFAULT now();
ALTER TABLE trekking_difficultylevel ALTER COLUMN date_update SET DEFAULT now();

-- WebLink
----------
-- name
-- url
-- category


-- WebLinkCategory
------------------
-- label
-- pictogram
ALTER TABLE trekking_weblinkcategory ALTER COLUMN date_insert SET DEFAULT now();
ALTER TABLE trekking_weblinkcategory ALTER COLUMN date_update SET DEFAULT now();

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
ALTER TABLE trekking_poi ALTER COLUMN provider SET DEFAULT '';

-- publication_date


-- POIType
----------
-- label
-- cirkwi
-- pictogram
ALTER TABLE trekking_poitype ALTER COLUMN date_insert SET DEFAULT now();
ALTER TABLE trekking_poitype ALTER COLUMN date_update SET DEFAULT now();

-- ServiceType
--------------
-- practices
-- pictogram
-- name
ALTER TABLE trekking_poi ALTER COLUMN review SET DEFAULT FALSE;
ALTER TABLE trekking_poi ALTER COLUMN published SET DEFAULT FALSE;
ALTER TABLE trekking_servicetype ALTER COLUMN date_insert SET DEFAULT now();
ALTER TABLE trekking_servicetype ALTER COLUMN date_update SET DEFAULT now();
-- publication_date


-- Service
----------
-- topo_object
-- type
--eid
--structure
ALTER TABLE trekking_service ALTER COLUMN provider SET DEFAULT '';
