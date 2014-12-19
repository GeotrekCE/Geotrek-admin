CREATE OR REPLACE VIEW geotrek.l_v_sentier AS (
    SELECT e.geom, t.*
    FROM l_t_sentier AS t, e_t_evenement AS e
    WHERE t.evenement = e.id
    AND e.supprime = FALSE
);
