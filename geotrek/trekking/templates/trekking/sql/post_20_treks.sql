CREATE FUNCTION {{ schema_geotrek }}.create_relationships_iu() RETURNS trigger SECURITY DEFINER AS $$
DECLARE
    t_count integer;
BEGIN
    IF TG_OP = 'UPDATE' THEN
        UPDATE trekking_trekrelationship SET has_common_departure = NEW.has_common_departure, has_common_edge = NEW.has_common_edge,
        is_circuit_step = NEW.is_circuit_step
        WHERE trek_a_id = NEW.trek_b_id AND trek_b_id = NEW.trek_a_id
          AND (has_common_departure != NEW.has_common_departure OR has_common_edge != NEW.has_common_edge OR is_circuit_step != NEW.is_circuit_step);
    ELSE
        SELECT COUNT(*) INTO t_count FROM trekking_trekrelationship WHERE trek_a_id = NEW.trek_b_id AND trek_b_id = NEW.trek_a_id;
        IF t_count = 0 THEN
            INSERT INTO trekking_trekrelationship (trek_a_id, trek_b_id, has_common_departure, has_common_edge, is_circuit_step)
            VALUES (NEW.trek_b_id, NEW.trek_a_id, NEW.has_common_departure, NEW.has_common_edge, NEW.is_circuit_step);
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER o_r_create_relationships_iu_tgr
AFTER INSERT OR UPDATE ON trekking_trekrelationship
FOR EACH ROW EXECUTE PROCEDURE create_relationships_iu();


CREATE FUNCTION {{ schema_geotrek }}.cleanup_relationships_d() RETURNS trigger SECURITY DEFINER AS $$
DECLARE
BEGIN
    DELETE FROM trekking_trekrelationship
    WHERE trek_a_id = OLD.trek_b_id
      AND trek_b_id = OLD.trek_a_id;
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER o_r_cleanup_relationships_d_tgr
AFTER DELETE ON trekking_trekrelationship
FOR EACH ROW EXECUTE PROCEDURE cleanup_relationships_d();
