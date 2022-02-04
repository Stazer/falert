<script>
    import Map from '../component/map/map.svelte';
    import MapPolygon from '../component/map/map-polygon.svelte';
    import MapPolygonVertex from '../component/map/map-polygon-vertex.svelte';

    let createSubscriptionOpen = false;
    let selectedVertices = [];

    const onClickCancel = () => {
        createSubscriptionOpen = false;
        selectedVertices = [];
    };

    const onClickCreateSubscription = () => {
        createSubscriptionOpen = true;
        selectedVertices = [];
    };

    const onClickReset = () => {
        selectedVertices = [];
    };

    const onClickMap = (event) => {
        if (createSubscriptionOpen === false) {
            return;
        }

        selectedVertices.push({
            latitude: event.detail.latitude,
            longitude: event.detail.longitude,
        });

        selectedVertices = selectedVertices;
    };
</script>

<div class="navbar shadow-lg bg-neutral text-neutral-content">
    <div class="flex-none px-2 mx-2">
        <span class="text-lg font-bold"> falert </span>
    </div>

    <div class="flex-1 px-2 mx-2">
        <button class="btn btn-ghost btn-sm rounded-btn" on:click={onClickCreateSubscription}>
            Create Subscription
        </button>
    </div>
</div>

<div class="h-full w-full" class:flex={createSubscriptionOpen}>
    {#if createSubscriptionOpen}
        <div class="basis-1/5 p-4">
            {#if selectedVertices.length > 0}
                <ul class="menu border bg-base-100 rounded-box">
                    {#each selectedVertices as vertex}
                        <li>
                            <a>
                                <div class="kbd mx-2">{vertex.longitude.toFixed(2)} lng</div>
                                <div class="kbd mx-2">{vertex.latitude.toFixed(2)} lat</div>
                            </a>
                        </li>
                    {/each}
                </ul>
            {/if}
            <div class="flex justify-center py-4">
                <div class="btn btn-ghost" on:click={onClickCancel}>Submit</div>
                <div class="btn btn-ghost" on:click={onClickCancel}>Cancel</div>
                <div class="btn btn-ghost" on:click={onClickReset}>Reset</div>
            </div>
        </div>
    {/if}
    <div class="h-full basis-4/5">
        <Map latitude={51.509} longitude={-0.08} on:click={onClickMap}>
            {#if createSubscriptionOpen}
                <MapPolygon color="red">
                    {#each selectedVertices as vertex}
                        <MapPolygonVertex longitude={vertex.longitude} latitude={vertex.latitude} />
                    {/each}
                </MapPolygon>
            {/if}
        </Map>
    </div>
</div>
