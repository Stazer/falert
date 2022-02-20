<script>
    import Map from '../component/map/map.svelte';
    import MapPolygon from '../component/map/map-polygon.svelte';
    import MapPolygonVertex from '../component/map/map-polygon-vertex.svelte';

    const createSubscriptionSidebarViewKey = 'createSubscription';
    const jumpToSidebarViewKey = 'jumpTo';

    let selectedVertices = [];
    let sidebarViewKey = null;
    let longitude = 13.404954;
    let latitude = 52.520008;
    let jumpToFormValues = {
        longitude: null,
        latitude: null,
    };

    const onClickCancel = () => {
        sidebarViewKey = null;
        selectedVertices = [];
    };

    const onClickCreateSubscription = () => {
        sidebarViewKey = createSubscriptionSidebarViewKey;
        selectedVertices = [];
    };

    const onClickReset = () => {
        selectedVertices = [];
    };

    const onClickMap = (event) => {
        if (sidebarViewKey !== createSubscriptionSidebarViewKey) {
            return;
        }

        selectedVertices.push({
            latitude: event.detail.latitude,
            longitude: event.detail.longitude,
        });

        selectedVertices = selectedVertices;
    };

    const onClickJumpTo = () => {
        sidebarViewKey = jumpToSidebarViewKey;
        jumpToFormValues = {
            longitude: null,
            latitude: null,
        };
    };

    const onClickSubmitJumpTo = () => {
        console.log('sad');
        longitude = jumpToFormValues.longitude;
        latitude = jumpToFormValues.latitude;
    };

    const onClickSubmitCreateSubscription = () => {
        fetch('http://localhost:8000/subscriptions', {
            method: 'POST',
            body: JSON.stringify({
                vertices: selectedVertices,
            }),
        }).then(() => {
            selectedVertices = [];
            sidebarViewKey = null;
        });
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
        <button class="btn btn-ghost btn-sm rounded-btn" on:click={onClickJumpTo}> Jump To </button>
    </div>
</div>

<div class="h-full w-full" class:flex={sidebarViewKey !== null}>
    {#if sidebarViewKey !== null}
        <div class="basis-1/5 p-4">
            {#if sidebarViewKey === createSubscriptionSidebarViewKey}
                {#if selectedVertices.length > 0}
                    <ul class="menu border bg-base-100 rounded-box">
                        {#each selectedVertices as vertex}
                            <li>
                                <div class="kbd mx-2">{vertex.longitude.toFixed(2)} lng</div>
                                <div class="kbd mx-2">{vertex.latitude.toFixed(2)} lat</div>
                            </li>
                        {/each}
                    </ul>
                {/if}
                <div class="flex justify-center py-4">
                    <div class="btn btn-ghost" on:click={onClickSubmitCreateSubscription}>
                        Submit
                    </div>
                    <div class="btn btn-ghost" on:click={onClickCancel}>Cancel</div>
                    <div class="btn btn-ghost" on:click={onClickReset}>Reset</div>
                </div>
            {/if}

            {#if sidebarViewKey === jumpToSidebarViewKey}
                <input
                    type="text"
                    bind:value={jumpToFormValues.latitude}
                    placeholder="Latitude"
                    class="input w-full max-w-xs"
                />
                <input
                    type="text"
                    bind:value={jumpToFormValues.longitude}
                    placeholder="Longitude"
                    class="input w-full max-w-xs"
                />
                <div class="btn btn-ghost" on:click={onClickSubmitJumpTo}>Jump To</div>
                <div class="btn btn-ghost" on:click={onClickCancel}>Cancel</div>
            {/if}
        </div>
    {/if}
    <div class="h-full basis-4/5">
        <Map {latitude} {longitude} on:click={onClickMap}>
            {#if selectedVertices.length > 0}
                <MapPolygon color="red">
                    {#each selectedVertices as vertex}
                        <MapPolygonVertex longitude={vertex.longitude} latitude={vertex.latitude} />
                    {/each}
                </MapPolygon>
            {/if}
        </Map>
    </div>
</div>
