-- InfrastructureType
---------------------
-- label
ALTER TABLE infrastructure_infrastructuretype ALTER COLUMN type SET DEFAULT 'A';
-- structure
-- pictogram

-- InfrastructureCondition
--------------------------
-- label
-- structure


-- InfrastructureMaintenanceDifficultyLevel
-------------------------------------------
-- label
-- structure


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
ALTER TABLE infrastructure_infrastructure ALTER COLUMN provider SET DEFAULT '';