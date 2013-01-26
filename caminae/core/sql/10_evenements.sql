-------------------------------------------------------------------------------
-- Add spatial index (will boost spatial filters)
-------------------------------------------------------------------------------

DROP INDEX IF EXISTS evenements_geom_idx;
CREATE INDEX evenements_geom_idx ON evenements USING gist(geom);


-------------------------------------------------------------------------------
-- Keep dates up-to-date
-------------------------------------------------------------------------------

DROP TRIGGER IF EXISTS evenements_date_insert_tgr ON evenements;
CREATE TRIGGER evenements_date_insert_tgr
    BEFORE INSERT ON evenements
    FOR EACH ROW EXECUTE PROCEDURE ft_date_insert();

DROP TRIGGER IF EXISTS evenements_date_update_tgr ON evenements;
CREATE TRIGGER evenements_date_update_tgr
    BEFORE INSERT OR UPDATE ON evenements
    FOR EACH ROW EXECUTE PROCEDURE ft_date_update();


-------------------------------------------------------------------------------
-- Update geometry when offset change
-------------------------------------------------------------------------------

DROP TRIGGER IF EXISTS evenements_offset_u_tgr ON evenements;

CREATE OR REPLACE FUNCTION update_evenement_geom_when_offset_changes() RETURNS trigger AS $$
BEGIN
    -- Note: We are using an "after" trigger here because the function below
    -- takes topology id as an argument and emits its own SQL queries to read
    -- and write data.
    -- Since the evenement to be modified is available in NEW, we could improve
    -- performance with some refactoring.
    PERFORM update_geometry_of_evenement(NEW.id);

    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER evenements_offset_u_tgr
AFTER UPDATE OF decallage ON evenements
FOR EACH ROW EXECUTE PROCEDURE update_evenement_geom_when_offset_changes();


-------------------------------------------------------------------------------
-- Delete related interventions when an evenement is deleted
-------------------------------------------------------------------------------

DROP TRIGGER IF EXISTS evenements_interventions_d_tgr ON evenements;

CREATE OR REPLACE FUNCTION delete_related_intervention() RETURNS trigger AS $$
BEGIN
    UPDATE m_t_intervention SET supprime = TRUE WHERE topology_id = OLD.id;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER evenements_interventions_d_tgr
AFTER UPDATE OF supprime ON evenements
FOR EACH ROW EXECUTE PROCEDURE delete_related_intervention();
