<script>
    import { createEventDispatcher, onMount, setContext } from 'svelte';
    import { browser } from '$app/env';

    import { key } from './map-context.js';

    export let longitude;
    export let latitude;
    export let zoom = 13;

    const dispatch = createEventDispatcher();

    const polygons = [];

    const addPolygon = (polygon) => {
        polygons.push(polygon);
    };

    const onClick = (event) => {
        dispatch('click', {
            longitude: event.latlng[0],
            latitude: event.latlng[1],
        });
    };

    setContext(key, {
        addPolygon,
    });

    onMount(async () => {
        if (browser) {
            const leaflet = await import('leaflet');

            const map = leaflet.map('map').setView([longitude, latitude], zoom);

            leaflet
                .tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                    attribution:
                        '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
                })
                .addTo(map);

            polygons
                .map((polygon) => {
                    return leaflet.polygon(
                        polygon.vertices.map((vertex) => {
                            return [vertex.longitude, vertex.latitude];
                        }),
                        {
                            color: polygon.color,
                        },
                    );
                })
                .forEach((polygon) => {
                    polygon.addTo(map);
                });

            map.on('click', onClick);
        }
    });
</script>

<div id="map" />

<slot />

<style>
    @import 'https://unpkg.com/leaflet@1.7.1/dist/leaflet.css';

    #map {
        height: 100%;
    }
</style>
