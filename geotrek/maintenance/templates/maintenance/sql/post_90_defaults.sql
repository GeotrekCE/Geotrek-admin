-- Intervention
---------------
-- name
ALTER TABLE maintenance_intervention ALTER COLUMN "begin_date" SET DEFAULT now();
ALTER TABLE maintenance_intervention ALTER COLUMN subcontracting SET DEFAULT FALSE;
ALTER TABLE maintenance_intervention ALTER COLUMN width SET DEFAULT 0.0;
ALTER TABLE maintenance_intervention ALTER COLUMN height SET DEFAULT 0.0;
ALTER TABLE maintenance_intervention ALTER COLUMN area SET DEFAULT 0;
ALTER TABLE maintenance_intervention ALTER COLUMN material_cost SET DEFAULT 0.0;
ALTER TABLE maintenance_intervention ALTER COLUMN heliport_cost SET DEFAULT 0.0;
ALTER TABLE maintenance_intervention ALTER COLUMN subcontract_cost SET DEFAULT 0.0;
-- stake
-- status
--type
-- disorders
-- jobs
-- project
ALTER TABLE maintenance_intervention ALTER COLUMN description SET DEFAULT '';
-- eid
ALTER TABLE maintenance_intervention ALTER COLUMN slope SET DEFAULT 0.0;
ALTER TABLE maintenance_intervention ALTER COLUMN min_elevation SET DEFAULT 0;
ALTER TABLE maintenance_intervention ALTER COLUMN max_elevation SET DEFAULT 0;
ALTER TABLE maintenance_intervention ALTER COLUMN ascent SET DEFAULT 0;
ALTER TABLE maintenance_intervention ALTER COLUMN descent SET DEFAULT 0;
ALTER TABLE maintenance_intervention ALTER COLUMN date_insert SET DEFAULT now();
ALTER TABLE maintenance_intervention ALTER COLUMN date_update SET DEFAULT now();
-- structure
-- deleted


-- InterventionStatus
---------------------
-- status
-- order
-- structure


-- InterventionType
-------------------
-- type
-- structure


-- InterventionDisorder
-----------------------
-- disorder
-- structure


-- InterventionJob
------------------
-- job
ALTER TABLE maintenance_interventionjob ALTER COLUMN cost SET DEFAULT 1.0;
ALTER TABLE maintenance_interventionjob ALTER COLUMN active SET DEFAULT True;
-- structure


-- ManDay
---------
-- nb_days
-- intervention
-- job


-- Project
-----------
-- name
-- begin_year
-- end_year
ALTER TABLE maintenance_project ALTER COLUMN "constraint" SET DEFAULT '';
ALTER TABLE maintenance_project ALTER COLUMN global_cost SET DEFAULT 0;
ALTER TABLE maintenance_project ALTER COLUMN comments SET DEFAULT '';
-- type
-- domain
-- contractors
-- project_owner
-- project_manager
-- founders
-- eid
ALTER TABLE maintenance_project ALTER COLUMN date_insert SET DEFAULT now();
ALTER TABLE maintenance_project ALTER COLUMN date_update SET DEFAULT now();
-- structure
-- deleted


-- ProjectType
--------------
-- type
-- structure


-- ProjectDomain
----------------
-- domain
-- structure


-- Contractor
-------------
-- contractor
-- structure


-- Funding
----------
-- amount
-- project
-- organism
