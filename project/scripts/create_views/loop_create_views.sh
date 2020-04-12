#!/bin/bash  

#sql_command=$(echo $sql_command | tr -d '/n')

for i in {00..23}
do
    #sql_command="DROP MATERIALIZED VIEW daten.avg_${i}_hrs"
    sql_command="CREATE MATERIALIZED VIEW daten.avg_${i}_hrs ( id_pk, station_id, avg_pm25, geom)AS WITH at_epoch AS (SELECT ld.station_id, ld.p25, lds.geom FROM daten.dt_luftdaten ld JOIN daten.lut_luftdaten_stations lds ON ld.station_id = lds.station_id WHERE date_part('hour'::text, ld.time_stamp) = $i::double precision AND ld.p10 <= (( SELECT percentile_disc(0.99::double precision) WITHIN GROUP ( ORDER BY dt_1.p10) AS perc FROM daten.dt_luftdaten dt_1 JOIN daten.lut_luftdaten_stations s_1 ON dt_1.station_id = s_1.station_id )) UNION ALL SELECT lu.station_id, lu.p25, lus.geom FROM daten.dt_luftdaten lu JOIN daten.lut_lubw_stations lus ON lu.station_id = lus.idpk WHERE date_part('hour'::text, lu.time_stamp) = $i::double precision ) SELECT row_number() OVER ()::integer AS id_pk, at_epoch.station_id, avg(at_epoch.p25) AS avg_pm25, at_epoch.geom FROM at_epoch GROUP BY at_epoch.station_id, at_epoch.geom;"
    echo "creating view for epoch $i"
    PGPASSWORD="postgres" psql -p "5430" -d "luftdaten" -U "postgres" -c "$sql_command"
done