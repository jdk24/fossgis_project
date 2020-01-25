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
                <!--                <l-geo-json-->
                <!--                        :geojson="geojson"-->
                <!--                        :options="onEachFeatureFunction"-->
                <!--                        :options-style="styleFunction"-->
                <!--                />-->
                <l-geo-json
                        :geojson="stuttgart.value"
                        :options="onEachFeatureFunction"
                        :options-style="styleFunction"
                />
                <l-geo-json
                        v-show="districts.show"
                        :geojson="districts_geojson"
                        :options="onEachFeatureFunction"
                        :options-style="styleFunction('hello')"
                />
                <l-geo-json
                        v-if="route !== null"
                        :geojson="routeLine"
                        :options="onEachFeatureFunction()"
                        :options-style="styleFunction('line')"
                />
                <l-marker v-for="m in markersList"
                          :draggable="true"
                          :lat-lng.sync="m.position"
                          @dragend="dragEnd()"
                >
                </l-marker>
            </l-map>
        </div>
        <div id="sidebar" class="sidebar" style="height: 100%; width: 25%; margin: 0;padding: 0; float: right">
            <input type="checkbox" v-model="districts.show">
            <input type="text" v-model="api_key">
        </div>
    </div>
</template>
<script src="./app.js">

</script>
<style>
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
        flex: auto;
        flex-direction: row;
    }
</style>
