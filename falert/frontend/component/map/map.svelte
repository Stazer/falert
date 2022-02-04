<script>
    import { beforeUpdate, afterUpdate, createEventDispatcher, onMount, setContext } from 'svelte';
    import { browser } from '$app/env';

    import { key } from './map-context.js';

    export let longitude;
    export let latitude;
    export let zoom = 13;

    const dispatch = createEventDispatcher();

    let polygons = new Map();

    let map = null;
    let leaflet = null;

    const setPolygon = (symbol, polygon) => {
        polygons.set(symbol, {
            ...polygon,
            handle: null,
        });
    };

    const deletePolygon = (symbol) => {
        polygons.delete(symbol);
    };

    const updatePolygon = (symbol) => {
        updatePolygons();
    };

    const onClick = (event) => {
        dispatch('click', {
            longitude: event.latlng.lng,
            latitude: event.latlng.lat,
        });
    };

    const updatePolygons = () => {
        if (leaflet === null || map === null) {
            return;
        }

        polygons.forEach((polygon) => {
            if (polygon.handle !== null) {
                polygon.handle.removeFrom(map);
            }

            polygon.handle = leaflet.polygon(
                Array.from(polygon.vertices.values(), (vertex) => {
                    return [vertex.latitude, vertex.longitude];
                }),
                {
                    color: polygon.color,
                },
            );

            if (polygon.handle !== null) {
                polygon.handle.addTo(map);
            }
        });
    };

    setContext(key, {
        setPolygon,
        deletePolygon,
        updatePolygon,
    });

    onMount(async () => {
        if (browser) {
            if (leaflet === null) {
                leaflet = await import('leaflet');
            }

            if (map === null) {
                map = leaflet.map('map').setView([latitude, longitude], zoom);
            }

            leaflet
                .tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                    attribution:
                        '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
                })
                .addTo(map);

            updatePolygons();

            map.on('click', onClick);
        }
    });

    beforeUpdate(() => {
        if (browser) {
            updatePolygons();
        }
    });

    afterUpdate(() => {
        if (browser) {
            updatePolygons();
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
