-- PhysicalType
---------------
-- name
-- structure

-- PhysicalEdge
---------------
-- topo_object
-- physical_type
-- eid

-- LandType
-----------
-- name
ALTER TABLE land_landtype ALTER COLUMN right_of_way SET DEFAULT False;
-- structure


-- LandEdge
-----------
-- topo_object
-- land_type
ALTER TABLE land_landedge ALTER COLUMN owner SET DEFAULT '';
ALTER TABLE land_landedge ALTER COLUMN agreement SET DEFAULT False;
-- eid


-- CompetenceEdge
-----------------
-- topo_object
-- organization
-- eid


-- WorkManagementEdge
---------------------
-- topo_object
-- organization
-- eid


-- SignageManagementEdge
------------------------
-- topo_object
-- organization
-- eid


-- InfrastructureUsageDifficultyLevel
-------------------------------------
-- label
-- structure


-- Infrastructure
-----------------
-- type
-- maintenance_difficulty
-- usage_difficulty
ALTER TABLE infrastructure_infrastructure ALTER COLUMN accessibility SET DEFAULT '';
-- topo_object
-- name
ALTER TABLE infrastructure_infrastructure ALTER COLUMN description SET DEFAULT '';
-- condition
-- implantation_year
-- eid
ALTER TABLE infrastructure_infrastructure ALTER COLUMN published SET DEFAULT FALSE;
-- publication_date
-- structure
