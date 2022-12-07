-- Path
-------
-- geom
-- geom_cadastre
ALTER TABLE core_path ALTER COLUMN valid SET DEFAULT true;
ALTER TABLE core_path ALTER COLUMN visible SET DEFAULT true;
ALTER TABLE core_path ALTER COLUMN name SET DEFAULT '';
ALTER TABLE core_path ALTER COLUMN comments SET DEFAULT '';
ALTER TABLE core_path ALTER COLUMN departure SET DEFAULT '';
ALTER TABLE core_path ALTER COLUMN arrival SET DEFAULT '';
-- comfort
-- source
-- stake
-- usages
-- networks
ALTER TABLE core_path ALTER COLUMN eid SET DEFAULT '';
ALTER TABLE core_path ALTER COLUMN draft SET DEFAULT False;
ALTER TABLE core_path ALTER COLUMN uuid SET DEFAULT gen_random_uuid();
-- geom_3d
ALTER TABLE core_path ALTER COLUMN "length" SET DEFAULT 0.0;
ALTER TABLE core_path ALTER COLUMN ascent SET DEFAULT 0.0;
ALTER TABLE core_path ALTER COLUMN descent SET DEFAULT 0;
ALTER TABLE core_path ALTER COLUMN min_elevation SET DEFAULT 0;
ALTER TABLE core_path ALTER COLUMN max_elevation SET DEFAULT 0;
ALTER TABLE core_path ALTER COLUMN slope SET DEFAULT 0.0;
ALTER TABLE core_path ALTER COLUMN date_insert SET DEFAULT now();
ALTER TABLE core_path ALTER COLUMN date_update SET DEFAULT now();
ALTER TABLE core_path ALTER COLUMN provider SET DEFAULT '';

-- structure


-- Topology
-----------
-- paths
ALTER TABLE core_topology ALTER COLUMN "offset" SET DEFAULT 0.0;
ALTER TABLE core_topology ALTER COLUMN kind SET DEFAULT '';
ALTER TABLE core_topology ALTER COLUMN "length" SET DEFAULT 0.0;
ALTER TABLE core_topology ALTER COLUMN geom_need_update SET DEFAULT FALSE;
-- geom
ALTER TABLE core_topology ALTER COLUMN uuid SET DEFAULT gen_random_uuid();
-- geom_3d
ALTER TABLE core_topology ALTER COLUMN ascent SET DEFAULT 0.0;
ALTER TABLE core_topology ALTER COLUMN descent SET DEFAULT 0;
ALTER TABLE core_topology ALTER COLUMN min_elevation SET DEFAULT 0;
ALTER TABLE core_topology ALTER COLUMN max_elevation SET DEFAULT 0;
ALTER TABLE core_topology ALTER COLUMN slope SET DEFAULT 0.0;
ALTER TABLE core_topology ALTER COLUMN date_insert SET DEFAULT now();
ALTER TABLE core_topology ALTER COLUMN date_update SET DEFAULT now();
ALTER TABLE core_topology ALTER COLUMN deleted SET DEFAULT False;


-- PathAggregation
------------------
-- path
-- topo_object
ALTER TABLE core_pathaggregation ALTER COLUMN start_position SET DEFAULT 0;
ALTER TABLE core_pathaggregation ALTER COLUMN end_position SET DEFAULT 0;
ALTER TABLE core_pathaggregation ALTER COLUMN "order" SET DEFAULT 0;


-- PathSource
-------------
-- source
-- structure

-- Stake
--------
-- stake
-- structure

-- Comfort
----------
-- comfort
-- structure

-- Usage
--------
-- stake
-- structure

-- Network
----------
-- network
-- structure


-- Trail
--------
-- topo_object
-- name
ALTER TABLE core_trail ALTER COLUMN departure SET DEFAULT '';
ALTER TABLE core_trail ALTER COLUMN arrival SET DEFAULT '';
ALTER TABLE core_trail ALTER COLUMN comments SET DEFAULT '';
ALTER TABLE core_trail ALTER COLUMN eid SET DEFAULT '';
ALTER TABLE core_trail ALTER COLUMN provider SET DEFAULT '';

-- structure
