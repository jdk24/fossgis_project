#!/bin/bash
# sudo chmod +x /etc/cron.hourly/dl_lubw.sh 
# Get data from public api. Exit if curl throws failure (http response!=2xx) 
while :
do
    OUTFILE=lubw_$(TZ=Europe/Berlin date +%Y%m%d_%H%M).geojson
    until curl --fail "https://lupo-messwerte.appspot.com/generic?table=bw_luft_stammdaten&limit=999&filter=aktiv:true;type:-Spot&order=NO2-today-latest-class" \
    -o lubw_dl/$OUTFILE;
    echo "$OUTFILE heruntergeladen"
    do  
        echo "$OUTFILE nicht heruntergeladen. Neuer Versuch in 30 Sekunden"
        sleep 30
    done

    "C:\OSGeo4W64\OSGeo4W.bat" ogr2ogr -f PostgreSQL PG:"dbname=luftdaten user=postgres port=5430 password="postgres" " "lubw_dl/$OUTFILE" -nln input_raw_lubw -overwrite --config OGR_TRUNCATE YES
    
    PGPASSWORD="postgres" psql -p 5430 -d luftdaten -U postgres -c "SELECT daten.lubw_parse()" 
    sleep 3600
done