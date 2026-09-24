CREATE TRIGGER zoning_city_date_update_tgr
    BEFORE INSERT OR UPDATE ON zoning_city
    FOR EACH ROW EXECUTE PROCEDURE ft_date_update();

CREATE TRIGGER zoning_district_date_update_tgr
    BEFORE INSERT OR UPDATE ON zoning_district
    FOR EACH ROW EXECUTE PROCEDURE ft_date_update();

CREATE TRIGGER zoning_restrictedarea_date_update_tgr
    BEFORE INSERT OR UPDATE ON zoning_restrictedarea
    FOR EACH ROW EXECUTE PROCEDURE ft_date_update();

CREATE TRIGGER zoning_vigilancearea_date_update_tgr
    BEFORE INSERT OR UPDATE ON zoning_vigilancearea
    FOR EACH ROW EXECUTE PROCEDURE ft_date_update();
