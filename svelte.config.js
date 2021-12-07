import adapter from '@sveltejs/adapter-auto';

/** @type {import('@sveltejs/kit').Config} */
const config = {
    kit: {
        adapter: adapter(),

        // hydrate the <div id="svelte"> element in src/app.html
        target: '#svelte',
        files: {
            template: 'falert/frontend/app.html',
            assets: 'falert/frontend/static',
            hooks: 'falert/frontend/hooks',
            lib: 'falert/frontend/lib',
            routes: 'falert/frontend/routes',
            serviceWorker: 'falert/frontend/service-worker',
        },
    },
};

export default config;
