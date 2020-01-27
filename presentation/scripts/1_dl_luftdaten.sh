#!/bin/bash
#
# sudo chmod +x /etc/cron.hourly/dl_lubw.sh 
# Get data from lufdaten api. 30s loop until curl dl exits without failure. 1h loop as workaround in case there's no cron/task manager/etc. 
while :
do
    OUTFILE=luftdaten_$(TZ=Europe/Berlin date +%Y%m%d_%H%M).geojson
    until curl --fail "https://data.sensor.community/static/v2/data.1h.json" \
    -o luftdaten_dl/$OUTFILE;
    echo "$OUTFILE heruntergeladen"
    do  
        echo "$OUTFILE nicht heruntergeladen. Neuer Versuch in 30 Sekunden"
        sleep 30
    done
    PGPASSWORD="postgres" psql -p 5430 -d luftdaten -U postgres -c "\copy input_raw_luftdaten FROM 'luftdaten_dl/$OUTFILE'"

    PGPASSWORD="postgres" psql -p 5430 -d luftdaten -U postgres -c "SELECT daten.luftdaten_parse()" 

    sleep 3600
done