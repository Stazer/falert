<script>
    import Map from '../component/map/map.svelte';
    import MapPolygon from '../component/map/map-polygon.svelte';
    import MapPolygonVertex from '../component/map/map-polygon-vertex.svelte';
</script>

<Map longitude={51.509} latitude={-0.08}>
    <MapPolygon>
        <MapPolygonVertex longitude={51.509} latitude={-0.08} />
        <MapPolygonVertex longitude={51.503} latitude={-0.06} />
        <MapPolygonVertex longitude={51.51} latitude={-0.047} />
    </MapPolygon>
</Map>
