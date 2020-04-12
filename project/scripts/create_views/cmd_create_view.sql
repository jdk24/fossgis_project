CREATE MATERIALIZED VIEW daten.avg_0_hrs (
    id_pk,
    station_id,
    avg_pm25,
    geom)
AS
 WITH at_epoch AS (
SELECT ld.station_id,
            ld.p25,
            lds.geom
FROM daten.dt_luftdaten ld
             JOIN daten.lut_luftdaten_stations lds ON ld.station_id = lds.station_id
WHERE date_part('hour'::text, ld.time_stamp) = 0::double precision
UNION ALL
SELECT lu.station_id,
            lu.p25,
            lus.geom
FROM daten.dt_luftdaten lu
             JOIN daten.lut_lubw_stations lus ON lu.station_id = lus.idpk
WHERE date_part('hour'::text, lu.time_stamp) = 0::double precision
        )
    SELECT row_number() OVER ()::integer AS id_pk,
    at_epoch.station_id,
    avg(at_epoch.p25) AS avg_pm25,
    at_epoch.geom
    FROM at_epoch
    GROUP BY at_epoch.station_id, at_epoch.geom;