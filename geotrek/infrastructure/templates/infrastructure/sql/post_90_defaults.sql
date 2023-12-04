-- InfrastructureType
---------------------
-- label
ALTER TABLE infrastructure_infrastructuretype ALTER COLUMN type SET DEFAULT 'A';
ALTER TABLE infrastructure_infrastructuretype ALTER COLUMN date_insert SET DEFAULT now();
ALTER TABLE infrastructure_infrastructuretype ALTER COLUMN date_update SET DEFAULT now();
-- structure
-- pictogram

-- InfrastructureAccessMean
----------
-- label
ALTER TABLE infrastructure_infrastructureaccessmean ALTER COLUMN date_insert SET DEFAULT now();
ALTER TABLE infrastructure_infrastructureaccessmean ALTER COLUMN date_update SET DEFAULT now();

-- InfrastructureCondition
--------------------------
-- label
-- structure
ALTER TABLE infrastructure_infrastructurecondition ALTER COLUMN date_insert SET DEFAULT now();
ALTER TABLE infrastructure_infrastructurecondition ALTER COLUMN date_update SET DEFAULT now();


-- InfrastructureMaintenanceDifficultyLevel
-------------------------------------------
-- label
-- structure
ALTER TABLE infrastructure_infrastructuremaintenancedifficultylevel ALTER COLUMN date_insert SET DEFAULT now();
ALTER TABLE infrastructure_infrastructuremaintenancedifficultylevel ALTER COLUMN date_update SET DEFAULT now();

-- InfrastructureUsageDifficultyLevel
-------------------------------------
-- label
-- structure
ALTER TABLE infrastructure_infrastructureusagedifficultylevel ALTER COLUMN date_insert SET DEFAULT now();
ALTER TABLE infrastructure_infrastructureusagedifficultylevel ALTER COLUMN date_update SET DEFAULT now();

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
ALTER TABLE infrastructure_infrastructure ALTER COLUMN provider SET DEFAULT '';
