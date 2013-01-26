
-------------------------------------------------------------------------------
-- Keep dates up-to-date
-------------------------------------------------------------------------------

DROP TRIGGER IF EXISTS m_t_intervention_date_insert_tgr ON m_t_intervention;
CREATE TRIGGER m_t_intervention_date_insert_tgr
    BEFORE INSERT ON m_t_intervention
    FOR EACH ROW EXECUTE PROCEDURE ft_date_insert();

DROP TRIGGER IF EXISTS m_t_intervention_date_update_tgr ON m_t_intervention;
CREATE TRIGGER m_t_intervention_date_update_tgr
    BEFORE INSERT OR UPDATE ON m_t_intervention
    FOR EACH ROW EXECUTE PROCEDURE ft_date_update();


DROP TRIGGER IF EXISTS m_t_chantier_date_update_tgr ON m_t_chantier;
CREATE TRIGGER m_t_chantier_date_update_tgr
    BEFORE INSERT OR UPDATE ON m_t_chantier
    FOR EACH ROW EXECUTE PROCEDURE ft_date_update();

DROP TRIGGER IF EXISTS m_t_chantier_date_update_tgr ON m_t_chantier;
CREATE TRIGGER m_t_chantier_date_update_tgr
    BEFORE INSERT OR UPDATE ON m_t_chantier
    FOR EACH ROW EXECUTE PROCEDURE ft_date_update();

-------------------------------------------------------------------------------
-- Delete related interventions when an evenement is deleted
-------------------------------------------------------------------------------

DROP TRIGGER IF EXISTS m_t_evenement_interventions_d_tgr ON e_t_evenement;

CREATE OR REPLACE FUNCTION delete_related_intervention() RETURNS trigger AS $$
BEGIN
    UPDATE m_t_intervention SET supprime = TRUE WHERE topology_id = OLD.id;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER m_t_evenement_interventions_d_tgr
AFTER UPDATE OF supprime ON e_t_evenement
FOR EACH ROW EXECUTE PROCEDURE delete_related_intervention();
