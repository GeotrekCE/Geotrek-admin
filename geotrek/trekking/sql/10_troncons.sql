SELECT create_schema_if_not_exist('rando');

DROP TRIGGER IF EXISTS l_t_unpublish_trek_d_tgr ON l_t_troncon;

CREATE OR REPLACE FUNCTION rando.troncons_unpublish_trek_d() RETURNS trigger AS $$
DECLARE
BEGIN
    -- Un-published treks because they might be broken
    UPDATE o_t_itineraire i
        SET public = FALSE
        FROM e_r_evenement_troncon et
        WHERE et.evenement = i.evenement AND et.troncon = OLD.id;


    IF {{PUBLISHED_BY_LANG}} THEN
        UPDATE o_t_itineraire i
            SET public_{{LANGUAGE_CODE}} = FALSE
            FROM e_r_evenement_troncon et
            WHERE et.evenement = i.evenement AND et.troncon = OLD.id;
    END IF;
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER l_t_unpublish_trek_d_tgr
BEFORE DELETE ON l_t_troncon
FOR EACH ROW EXECUTE PROCEDURE troncons_unpublish_trek_d();
