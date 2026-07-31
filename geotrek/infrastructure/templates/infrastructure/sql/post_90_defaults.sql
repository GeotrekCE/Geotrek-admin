-- InfrastructureType
---------------------
-- label
ALTER TABLE infrastructure_infrastructuretype ALTER COLUMN type SET DEFAULT 'A';
-- structure
-- pictogram


-- Infrastructure
-----------------
-- type
-- maintenance_difficulty
-- usage_difficulty
ALTER TABLE infrastructure_infrastructure ALTER COLUMN accessibility SET DEFAULT '';
-- topo_object
-- name
-- access
ALTER TABLE infrastructure_infrastructure ALTER COLUMN description SET DEFAULT '';
-- condition
-- implantation_year
-- eid
ALTER TABLE infrastructure_infrastructure ALTER COLUMN published SET DEFAULT FALSE;
-- publication_date
-- structure
