CREATE OR REPLACE FUNCTION {{ schema_geotrek }}.paths_unpublish_trek_d() RETURNS trigger SECURITY DEFINER AS $$
DECLARE
BEGIN
    -- Un-published treks because they might be broken
    UPDATE trekking_trek i
        SET published = FALSE
        FROM core_pathaggregation et
        WHERE et.topo_object_id = i.topo_object_id AND et.path_id = OLD.id;


    IF {{ PUBLISHED_BY_LANG }} THEN
        UPDATE trekking_trek i
        SET {% for lang in MODELTRANSLATION_LANGUAGES %}published_{{ lang }} = FALSE{% if not forloop.last %}, {% endif %}{% endfor %}
        FROM core_pathaggregation et
        WHERE et.topo_object_id = i.topo_object_id AND et.path_id = OLD.id;
    END IF;
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER l_t_unpublish_trek_d_tgr
BEFORE DELETE ON core_path
FOR EACH ROW EXECUTE PROCEDURE paths_unpublish_trek_d();
