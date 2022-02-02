<script>
    import { getContext, onMount } from 'svelte';

    import { key } from './map-polygon-context.js';

    const { addVertex } = getContext(key);

    export let longitude;
    export let latitude;

    onMount(() => {
        addVertex(longitude, latitude);
    });
</script>
