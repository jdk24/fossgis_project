import Vue from 'vue'

import App from './App.vue'
Vue.config.productionTip = false

/**
 * Fix Vue leaflet issues:
 * - import leaflet styles for proper map rendering
 * - edit marker image path
 */
import 'leaflet/dist/leaflet.css'
import L from 'leaflet'

delete L.Icon.Default.prototype._getIconUrl

L.Icon.Default.mergeOptions({
    iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
    iconUrl: require('leaflet/dist/images/marker-icon.png'),
    shadowUrl: require('leaflet/dist/images/marker-shadow.png')
})


new Vue({
    render: h => h(App),
}).$mount('#app')
