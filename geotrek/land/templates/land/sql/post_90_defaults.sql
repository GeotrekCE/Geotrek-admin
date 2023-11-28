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

-- CirculationType
-----------
-- name
-- structure

-- AuthorizationType
-----------
-- name
-- structure


-- CirculationEdge
-----------
-- topo_object
-- circulation_type
-- authorization_type
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
