DROP TRIGGER IF EXISTS o_r_create_relationships_iu_tgr ON o_r_itineraire_itineraire;

CREATE OR REPLACE FUNCTION rando.create_relationships_iu() RETURNS trigger AS $$
DECLARE
    t_count integer;
BEGIN
    IF TG_OP = 'UPDATE' THEN
        UPDATE o_r_itineraire_itineraire SET depart_commun = NEW.depart_commun, troncons_communs = NEW.troncons_communs, etape_circuit = NEW.etape_circuit
        WHERE itineraire_a = NEW.itineraire_b AND itineraire_b = NEW.itineraire_a
          AND (depart_commun != NEW.depart_commun OR troncons_communs != NEW.troncons_communs OR etape_circuit != NEW.etape_circuit);
    ELSE
        SELECT COUNT(*) INTO t_count FROM o_r_itineraire_itineraire WHERE itineraire_a = NEW.itineraire_b AND itineraire_b = NEW.itineraire_a;
        IF t_count = 0 THEN
            INSERT INTO o_r_itineraire_itineraire (itineraire_a, itineraire_b, depart_commun, troncons_communs, etape_circuit)
            VALUES (NEW.itineraire_b, NEW.itineraire_a, NEW.depart_commun, NEW.troncons_communs, NEW.etape_circuit);
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER o_r_create_relationships_iu_tgr
AFTER INSERT OR UPDATE ON o_r_itineraire_itineraire
FOR EACH ROW EXECUTE PROCEDURE create_relationships_iu();


DROP TRIGGER IF EXISTS o_r_cleanup_relationships_d_tgr ON o_r_itineraire_itineraire;

CREATE OR REPLACE FUNCTION rando.cleanup_relationships_d() RETURNS trigger AS $$
DECLARE
BEGIN
    DELETE FROM o_r_itineraire_itineraire
    WHERE itineraire_a = OLD.itineraire_b
      AND itineraire_b = OLD.itineraire_a;
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER o_r_cleanup_relationships_d_tgr
AFTER DELETE ON o_r_itineraire_itineraire
FOR EACH ROW EXECUTE PROCEDURE cleanup_relationships_d();
