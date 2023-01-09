-------------------------------------------------------------------------------
-- Compute elevation and elevation-based indicators
-------------------------------------------------------------------------------


CREATE TRIGGER outdoor_site_30_geometrycollection_flatten_iu_tgr
BEFORE INSERT OR UPDATE OF geom ON outdoor_site
FOR EACH ROW EXECUTE PROCEDURE flatten_geometrycollection_iu();

CREATE TRIGGER outdoor_course_30_geometrycollection_flatten_iu_tgr
BEFORE INSERT OR UPDATE OF geom ON outdoor_course
FOR EACH ROW EXECUTE PROCEDURE flatten_geometrycollection_iu();
