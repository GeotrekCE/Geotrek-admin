-------------------------------------------------------------------------------
-- Automatic link between Troncon and Commune/Zonage/Secteur
-------------------------------------------------------------------------------

DROP TRIGGER IF EXISTS troncons_couches_sig_d_tgr ON evenements_troncons;

CREATE OR REPLACE FUNCTION lien_auto_troncon_couches_sig_d() RETURNS trigger AS $$
DECLARE
    tab varchar;
BEGIN
    FOREACH tab IN ARRAY ARRAY[['commune', 'secteur', 'zonage']]
    LOOP
        -- Delete related object in association tables
        EXECUTE 'DELETE FROM '|| quote_ident(tab) ||' WHERE evenement = $1' USING OLD.evenement;
        -- Related evenement will be cleared by a more general trigger
    END LOOP;

    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER troncons_couches_sig_d_tgr
AFTER DELETE ON evenements_troncons
FOR EACH ROW EXECUTE PROCEDURE lien_auto_troncon_couches_sig_d();
