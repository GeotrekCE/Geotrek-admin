
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
