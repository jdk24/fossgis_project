import * as L from "leaflet"
import {LMap, LTileLayer, LGeoJson, LPopup, LMarker} from "vue2-leaflet"
import VueSlider from "vue-slider-component"
import axios from "axios"
import geojson from "./static/stuttgart"
import avoids from "./static/avoids"


let ors = require("openrouteservice-js")

export default {
    components: {
        "l-map": LMap, "l-tile-layer": LTileLayer, "l-geo-json": LGeoJson, "l-popup": LPopup, "l-marker": LMarker,
        "v-slider": VueSlider
    }, data() {
        return {
            routeInstance: null,
            url: "http://{s}.tile.osm.org/{z}/{x}/{y}.png",
            zoom: 13,
            bounds: L.latLngBounds(L.latLng(48.602794, 8.882591), L.latLng(48.945522, 9.539593)),
            attribution: "&copy; <a href=\"http://osm.org/copyright\">OpenStreetMap</a> contributors",
            style: {
                weight: 2, color: "#ECEFF1", opacity: 1, fillOpacity: 1
            },
            geojson: geojson,
            enableTooltip: false,
            color: "#5175ff",
            fillColor: "#5175ff",
            districts: {
                show: false,
                url: "http://localhost:8080/geoserver/project/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=project%3Astuttgart_districts&maxFeatures=50&outputFormat=application%2Fjson",
                value: null
            },
            stuttgart: {
                show: false,
                url: "http://localhost:8080/geoserver/project/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=project%3Astuttgart&maxFeatures=50&outputFormat=application%2Fjson",
                value: null
            },
            pm_10: {
                show: false,
                url: "http://localhost:8080/geoserver/project/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=project%3Apm10_view&outputFormat=application%2Fjson",
                value: null
            },
            route: null,
            api_key: "5b3ce3597851110001cf62483a54ed1a0e2342048e6c89f8c2f42286",
            markers: [],
            contextMenu: false,
            start: false,
            avoids: avoids,
            avoid_category: 2,
            pm: 'very low',
            hour: 12

        }
    }, created() {

    }, methods: {
        hourSliderLable() {
            return (val) => {
                return [0, 6, 12, 18, 23].includes(val)
            }
        },
        dragEnd() {
            this.computeRoute()
        }, rightClick(event) {
            this.eventPosition = event.latlng
            this.start = !this.start
            if (this.markers.length === 2) {
                this.markers[this.start ? 0 : 1] = {position: event.latlng}
                this.computeRoute()
            } else {
                this.markers.push({position: event.latlng})
                if (this.markers.length === 2) {
                    this.computeRoute()
                }
            }
        }, computeRoute() {
            let context = this
            setTimeout(() => {
                let start = this.markers[0]
                let end = this.markers[1]
                this.routeInstance.calculate({
                    coordinates: [[start.position.lng, start.position.lat], [end.position.lng, end.position.lat]],
                    profile: "cycling-regular",
                    avoid_polygons: this.avoidPolygons,
                    format: "geojson",
                    instructions: false
                }).then(function (json) {
                    context.route = json.features[0].geometry
                }).catch(function (err) {
                    let str = "An error occured: " + err
                    console.log(str)
                })
            }, 300)
        }
    }, computed: {
        avoidPolygons() {
            let coordinates = []
            for (let f of avoids.features) {
                if (Math.floor(f.properties.value) === this.avoid_category) {
                    coordinates.push(f.geometry.coordinates)
                }
            }
            return {
                type: 'MultiPolygon',
                coordinates: coordinates
            }
        },
        markersList() {
            return this.markers
        }, routeLine() {
            return this.route
        }, styleFunction() {
            const fillColor = this.fillColor

            return (obj) => {
                if (obj === "line") {
                    return {
                        weight: 4, color: "#10b617", opacity: 0.8
                    }
                } else if (obj === "avoid") {
                    return {
                        weight: 2, color: "#f14159", opacity: 0.7, fillColor: "#f14159", fillOpacity: 0.2
                    }
                } else {
                    return {
                            weight: 2, color: "#ECEFF1", opacity: 0.7, fillColor: fillColor, fillOpacity: 0.2
                    }
                }
            }

        }, onEachFeatureFunction() {
            if (!this.enableTooltip) {
                return () => {
                }
            }
            return (feature, layer) => {
                layer.bindTooltip("<div>code:" + feature + "</div>", {
                    permanent: false, sticky: true
                })
            }
        }, districts_geojson() {
            return this.districts.value
        }
    }, mounted() {
        let context = this
        this.routeInstance = new ors.Directions({api_key: this.api_key})
        axios.get(context.districts.url, {
            transformResponse: undefined, headers: {
                "Access-Control-Allow-Origin": "*", crossdomain: true
            }
        }).then(response => {
            context.districts.value = response.data.features[0]
            context.districts.show = true

        }).catch(error => {
            console.log('Stuttgart districts could not be loaded.', error.message, '. Check if geoserver is running.')
        })
        axios.get(context.stuttgart.url, {
            transformResponse: undefined, headers: {
                "Access-Control-Allow-Origin": "*", crossdomain: true
            }
        }).then(response => {
            context.stuttgart.value = response.data.features[0]
            context.stuttgart.show = true

        }).catch(error => {
            console.log('Stuttgart boundary could not be loaded.', error.message, '. Check if geoserver is running.')
        })
    }
}