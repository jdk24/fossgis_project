<template>
    <div id="app" class="app" style="height: 100%; width: 100%; margin: 0;padding: 0">
        <div style="height: 100%; width: 75%; margin: 0;padding: 0">
            <l-map
                    style="height: 100%; width: 100%"
                    :zoom="zoom"
                    :bounds="bounds"
                    :maxBounds="bounds"
                    :minZoom="11"
                    :maxZoom="18"
                    @click.right="rightClick($event)"
            >
                <l-tile-layer :url="url"
                              :attribution="attribution"/>
                <l-geo-json
                        v-if="stuttgart.show"
                        :geojson="stuttgart.value"
                        :options="onEachFeatureFunction()"
                        :options-style="styleFunction"
                />
                <l-geo-json
                        :geojson="avoidPolygons"
                        :options="onEachFeatureFunction()"
                        :options-style="styleFunction('avoid')"
                />
                <l-geo-json
                        v-if="route !== null"
                        :geojson="routeLine"
                        :options="onEachFeatureFunction()"
                        :options-style="styleFunction('line')"
                />
                <l-marker v-for="(m,i) in markersList"
                          :draggable="true"
                          :lat-lng.sync="m.position"
                          @dragend="dragEnd()"
                          :key="'marker-'+i"
                >
                </l-marker>
            </l-map>
        </div>
        <div id="sidebar" class="sidebar" style="height: 100%; width: 25%; margin: 0;padding: 0; float: right">
            <input type="checkbox" v-model="stuttgart.show">
            <input type="text" v-model="api_key">
            <v-slider
                    v-model="pm"
                    :tick-labels="['very low', 'low','medium', 'high', 'very high']"
                    :max="3"
                    step="1"
                    ticks="always"
                    tick-size="2"
            ></v-slider>
        </div>
    </div>
</template>
<script src="./app.js">

</script>
<style>
    @import '~vuetify/dist/vuetify.css';

    body {
        padding: 0;
        margin: 0;
    }

    html, body {
        height: 100%;
        width: 100%;
        margin: 0;
    }

    .app {
        display: flex;
        flex-direction: row;
    }

    .sidebar {
        display: flex;
        flex-direction: column;
    }
</style>
