-- Initial data taken from RPS ShapeFile with the command:
-- ogr2ogr -nlt MULTILINESTRING -a_srs EPSG:2154 -f PostgreSQL PG:"dbname=caminae port=5433 user=gba host=localhost" rps/rps.shp

-- Fix broken lines
UPDATE rps SET wkb_geometry = ST_Multi(ST_LineMerge(ST_Collect(ARRAY[ST_GeometryN(wkb_geometry, 1), ST_GeometryN(wkb_geometry, 3), ST_GeometryN(wkb_geometry, 6)]))) WHERE ogc_fid = 1874;
UPDATE rps SET wkb_geometry = ST_Multi(ST_LineMerge(ST_Collect(ARRAY[ST_RemovePoint(ST_GeometryN(wkb_geometry, 1), 0), ST_GeometryN(wkb_geometry, 2)]))) WHERE ogc_fid = 1866;
UPDATE rps SET wkb_geometry = ST_Multi(ST_LineMerge(ST_Collect(ARRAY[ST_SetPoint(ST_GeometryN(wkb_geometry, 1), 0, ST_EndPoint(ST_GeometryN(wkb_geometry, 2))), ST_GeometryN(wkb_geometry, 2)]))) WHERE ogc_fid = 1855;
UPDATE rps SET wkb_geometry = ST_Multi(ST_LineMerge(ST_Collect(ARRAY[ST_SetPoint(ST_GeometryN(wkb_geometry, 1), ST_NumPoints(ST_GeometryN(wkb_geometry, 1))-1, ST_StartPoint(ST_GeometryN(wkb_geometry, 2))), ST_GeometryN(wkb_geometry, 2)]))) WHERE ogc_fid = 1794;
UPDATE rps SET wkb_geometry = ST_Multi(ST_LineMerge(ST_Collect(ARRAY[ST_SetPoint(ST_GeometryN(wkb_geometry, 1), ST_NumPoints(ST_GeometryN(wkb_geometry, 1))-1, ST_StartPoint(ST_GeometryN(wkb_geometry, 2))), ST_GeometryN(wkb_geometry, 2)]))) WHERE ogc_fid = 1799;
UPDATE rps SET wkb_geometry = ST_Multi(ST_LineMerge(ST_Collect(ARRAY[ST_SetPoint(ST_GeometryN(wkb_geometry, 1), ST_NumPoints(ST_GeometryN(wkb_geometry, 1))-1, ST_EndPoint(ST_GeometryN(wkb_geometry, 2))), ST_GeometryN(wkb_geometry, 2)]))) WHERE ogc_fid = 1815;
UPDATE rps SET wkb_geometry = ST_Multi(ST_LineMerge(ST_Collect(ARRAY[ST_SetPoint(ST_GeometryN(wkb_geometry, 1), ST_NumPoints(ST_GeometryN(wkb_geometry, 1)) - 1, ST_EndPoint(ST_GeometryN(wkb_geometry, 2))), ST_GeometryN(wkb_geometry, 2)]))) WHERE ogc_fid = 1893;

-- Switch to simple linestrings
ALTER TABLE rps ADD geom Geometry(LINESTRING, 2154);
UPDATE rps SET geom = ST_GeometryN(wkb_geometry, 1);

-- Fix overlapping lines (1)
UPDATE rps t1 SET geom = ST_AddPoint(ST_AddPoint(t1.geom, ST_PointN(t2.geom, 2), 0), ST_PointN(t2.geom, 3), 0) FROM rps t2 WHERE t1.ogc_fid = 1796 AND t2.ogc_fid = 1799;
UPDATE rps SET geom = ST_RemovePoint(geom, ST_NumPoints(geom) - 1) WHERE ogc_fid = 1795;
UPDATE rps SET geom = ST_RemovePoint(ST_RemovePoint(geom, 0), 0) WHERE ogc_fid = 1799;
-- Fix overlapping lines (2)
UPDATE rps SET geom = ST_RemovePoint(geom, ST_NumPoints(geom) - 1) WHERE ogc_fid = 1878;
UPDATE rps SET geom = ST_RemovePoint(geom, 0) WHERE ogc_fid = 1877;
UPDATE rps t1 SET geom = ST_AddPoint(t1.geom, ST_EndPoint(t2.geom), -1) FROM rps t2 WHERE t1.ogc_fid = 1876 AND t2.ogc_fid = 1878;

-- Locate and register intersection
CREATE TABLE node (id serial PRIMARY KEY, geom Geometry(POINT, 2154));
INSERT INTO node(geom) SELECT ST_StartPoint(geom) AS geom FROM rps UNION SELECT ST_EndPoint(geom) AS geom FROM rps;
ALTER TABLE rps ADD node_start integer REFERENCES node(id);
ALTER TABLE rps ADD node_end integer REFERENCES node(id);
UPDATE rps SET node_start = node.id FROM node WHERE ST_Equals(ST_StartPoint(rps.geom), node.geom);
UPDATE rps SET node_end = node.id FROM node WHERE ST_Equals(ST_EndPoint(rps.geom), node.geom);

-- Improve line connexion
-- Locate intersections which are within a 10m range from one another
ALTER TABLE node ADD weird integer DEFAULT 0;
UPDATE node SET weird = zarb.nb FROM (SELECT ST_SnapToGrid(geom, 10) as geom, count(*) AS nb FROM node GROUP BY ST_SnapToGrid(geom, 10) HAVING count(*) > 1) AS zarb WHERE ST_Equals(ST_SnapToGrid(node.geom, 10), zarb.geom);
-- Fix poor connexion (1)
UPDATE rps SET geom = ST_RemovePoint(geom, 0) WHERE ogc_fid = 1883;
UPDATE rps SET node_start = 7 WHERE ogc_fid = 1883;
UPDATE rps SET geom = ST_AddPoint(rps.geom, node.geom, -1), node_end = node.id FROM node WHERE rps.ogc_fid = 1882 AND node.id = 7;
DELETE FROM node WHERE id = 8;
UPDATE node SET weird = 0 WHERE id = 7;
-- Fix poor connexion (2)
UPDATE rps SET geom = ST_AddPoint(ST_RemovePoint(rps.geom, 0), node.geom, 0), node_start = node.id FROM node WHERE node.id = 506 AND ogc_fid = 1850;
DELETE FROM node WHERE id = 505;
UPDATE node SET weird = 0 WHERE id = 506;
-- Fix poor connexion (3)
UPDATE rps SET geom = ST_AddPoint(rps.geom, node.geom, 0), node_start = node.id FROM node WHERE node.id = 785 AND rps.ogc_fid = 1824;
UPDATE rps SET geom = ST_AddPoint(rps.geom, node.geom, -1), node_end = node.id FROM node WHERE rps.ogc_fid = 1822 AND node.id = 785;
DELETE FROM rps WHERE ogc_fid = 1823;
DELETE FROM node WHERE id in (783, 784);
UPDATE node SET weird = 0 WHERE id = 785;
-- Fix poor connexion (4)
UPDATE rps SET geom = ST_AddPoint(ST_RemovePoint(rps.geom, ST_NumPoints(rps.geom) - 1), node.geom, -1), node_end = node.id FROM node WHERE rps.ogc_fid = 1874 AND node.id = 19;
DELETE FROM node WHERE id = 18;
UPDATE node SET weird = 0 WHERE id = 19;
-- Clean up
ALTER TABLE node DROP weird;

-- Simplify network
-- Locate vertices connecting exactly 2 edges
ALTER TABLE node ADD edge_count integer DEFAULT 0;
UPDATE node SET edge_count = n.nb FROM (SELECT id, count(*) as nb FROM (SELECT node_end as id FROM rps UNION ALL SELECT node_start as id FROM rps) as rps_nodes GROUP BY id) as n WHERE n.id = node.id;
-- => No network simplifcation, it's a huge work for a small benefit

-- Dump RPS dataset in the Django model
INSERT INTO troncons (date_insert, date_update, troncon_valide, longueur, denivelee_positive, denivelee_negative, altitude_minimum, altitude_maximum, geom) SELECT now(), now(), TRUE, ST_Length(geom), 0, 0, 0, 0, geom FROM rps;
