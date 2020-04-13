--Luftdaten vs. LUBW coefficient

WITH data as 
(
SELECT
d_lubw.ts,
d_luft.time_stamp,
d_lubw.p10,
d_luft.p10,
date_trunc('day',d_lubw.time_stamp) as daily,
(avg(d_luft.p10) over (order by d_lubw.time_stamp desc RANGE BETWEEN '1 day' PRECEDING AND CURRENT ROW))/(avg(d_lubw.p10) over (order by d_lubw.time_stamp desc RANGE BETWEEN '1 day' PRECEDING AND CURRENT ROW)) as factor


FROM daten.lut_lubw_stations l_lubw
cross JOIN daten.lut_luftdaten_stations l_luft
JOIN daten.dt_lubw d_lubw on l_lubw.idpk = d_lubw.fk_station_id
JOIN daten.dt_luftdaten d_luft on l_luft.station_id = d_luft.station_id
WHERE ST_DistanceSphere(l_lubw.geom, l_luft.geom) <= 1000
AND d_lubw.time_stamp = d_luft.time_stamp
--LIMIT 1000
--GROUP BY 
)

SELECT distinct on (daily) daily as time, 
factor
from data
group by daily, factor
ORDER BY daily asc