<script>
    import { getContext, setContext, onMount } from 'svelte';

    import { key as mapKey } from './map-context.js';
    import { key as mapPolygonKey } from './map-polygon-context.js';

    export let color = 'blue';

    const vertices = [];

    const addVertex = (longitude, latitude) => {
        vertices.push({
            longitude,
            latitude,
        });
    };

    const { addPolygon } = getContext(mapKey);

    setContext(mapPolygonKey, {
        addVertex,
    });

    onMount(() => {
        addPolygon({ vertices, color });
    });
</script>

<slot />
