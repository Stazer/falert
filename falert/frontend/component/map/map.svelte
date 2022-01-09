<script>
    import { onMount, setContext } from 'svelte';
    import { browser } from '$app/env';

    onMount(async () => {
        if(browser) {
            const leaflet = await import('leaflet');

            const map = leaflet.map('map').setView([52.518611, 13.408333], 13);

            leaflet.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            }).addTo(map);
        }
    });
</script>

<style>
    @import 'https://unpkg.com/leaflet@1.7.1/dist/leaflet.css';

    #map {
        height: 100%;
    }
</style>

<div id="map"></div>
