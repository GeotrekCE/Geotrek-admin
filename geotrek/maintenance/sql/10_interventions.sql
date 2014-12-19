SELECT create_schema_if_not_exist('gestion');

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

CREATE OR REPLACE FUNCTION gestion.delete_related_intervention() RETURNS trigger AS $$
BEGIN
    UPDATE m_t_intervention SET supprime = NEW.supprime WHERE topology_id = NEW.id;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER m_t_evenement_interventions_d_tgr
AFTER UPDATE OF supprime ON e_t_evenement
FOR EACH ROW EXECUTE PROCEDURE delete_related_intervention();


-------------------------------------------------------------------------------
-- Denormalized altimetry information
-------------------------------------------------------------------------------

ALTER TABLE m_t_intervention ALTER COLUMN longueur SET DEFAULT 0.0;
ALTER TABLE m_t_intervention ALTER COLUMN pente SET DEFAULT 0.0;
ALTER TABLE m_t_intervention ALTER COLUMN altitude_minimum SET DEFAULT 0;
ALTER TABLE m_t_intervention ALTER COLUMN altitude_maximum SET DEFAULT 0;
ALTER TABLE m_t_intervention ALTER COLUMN denivelee_positive SET DEFAULT 0;
ALTER TABLE m_t_intervention ALTER COLUMN denivelee_negative SET DEFAULT 0;

DROP TRIGGER IF EXISTS m_t_evenement_interventions_iu_tgr ON e_t_evenement;

CREATE OR REPLACE FUNCTION gestion.update_altimetry_evenement_intervention() RETURNS trigger AS $$
BEGIN
    UPDATE m_t_intervention SET
        longueur = CASE WHEN ST_GeometryType(NEW.geom) <> 'ST_Point' THEN NEW.longueur ELSE longueur END,
        pente = NEW.pente,
        altitude_minimum = NEW.altitude_minimum, altitude_maximum = NEW.altitude_maximum,
        denivelee_positive = NEW.denivelee_positive, denivelee_negative = NEW.denivelee_negative
     WHERE topology_id = NEW.id;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER m_t_evenement_interventions_iu_tgr
AFTER UPDATE OF longueur, pente,
    altitude_minimum, altitude_maximum,
    denivelee_positive, denivelee_negative ON e_t_evenement
FOR EACH ROW EXECUTE PROCEDURE update_altimetry_evenement_intervention();


DROP TRIGGER IF EXISTS m_t_intervention_altimetry_iu_tgr ON m_t_intervention;

CREATE OR REPLACE FUNCTION gestion.update_altimetry_intervention() RETURNS trigger AS $$
DECLARE
    elevation elevation_infos;
BEGIN
    SELECT geom_3d, pente, altitude_minimum, altitude_maximum, denivelee_positive, denivelee_negative
    FROM e_t_evenement WHERE id = NEW.topology_id INTO elevation;

    IF ST_GeometryType(elevation.draped) <> 'ST_Point' THEN
        NEW.longueur := ST_3DLength(elevation.draped);
    END IF;
    NEW.geom_3d := elevation.draped;
    NEW.pente := elevation.slope;
    NEW.altitude_minimum := elevation.min_elevation;
    NEW.altitude_maximum := elevation.max_elevation;
    NEW.denivelee_positive := elevation.positive_gain;
    NEW.denivelee_negative := elevation.negative_gain;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER m_t_intervention_altimetry_iu_tgr
BEFORE INSERT OR UPDATE OF topology_id ON m_t_intervention
FOR EACH ROW EXECUTE PROCEDURE update_altimetry_intervention();


-------------------------------------------------------------------------------
-- Compute area
-------------------------------------------------------------------------------

DROP TRIGGER IF EXISTS m_t_evenement_interventions_area_iu_tgr ON m_t_intervention;
DROP TRIGGER IF EXISTS m_t_intervention_area_iu_tgr ON m_t_intervention;

CREATE OR REPLACE FUNCTION gestion.update_area_intervention() RETURNS trigger AS $$
BEGIN
   NEW.surface := NEW.largeur * NEW.longueur;
   RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER m_t_intervention_area_iu_tgr
BEFORE INSERT OR UPDATE OF largeur, hauteur ON m_t_intervention
FOR EACH ROW EXECUTE PROCEDURE update_area_intervention();
