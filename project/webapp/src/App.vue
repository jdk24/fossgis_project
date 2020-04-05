<template>
    <div id="app" class="app" >
        <div class="map">
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
        <div id="sidebar" class="sidebar" style="">
            <h3>Healthy routing</h3>
            Find a healthy bicycle route through Stuttgart city using openrouteservice by avoiding areas of higher
            particulate matter concentration.
            <input type="checkbox" v-model="stuttgart.show">
            <input type="text" v-model="api_key">
            <div> Particle matter concentration to avoid</div>
            <v-slider
                    id="pm-slider"
                    class="slider"
                    v-model="pm"
                    :data="['very low', 'low','medium', 'high', 'very high']"
                    :ticks="'always'"
                    :tooltip="'none'"
                    :duration="0.3"
                    :marks="true"
                    :adsorb="true"
                    :tick-size="2"
                    :width="'80%'"
                    :height="'5px'"
                    :useKeyboard="true"
            ></v-slider>
            <div> Time of the day
            </div>
            <v-slider
                    class="slider"
                    v-model="hour"
                    :data="Array.from({length:24},(v,k)=>k)"
                    :ticks="'always'"
                    :tooltip="'focus'"
                    :duration="0.3"
                    :marks="hourSliderLable()"
                    :adsorb="true"
                    :tick-size="2"
                    :width="'80%'"
                    :height="'5px'"
                    :useKeyboard="true"
            ></v-slider>
        </div>
    </div>
</template>
<script src="./app.js">

</script>
<style>
    @import '~vue-slider-component/theme/default.css';
    @import 'app.css';
</style>
