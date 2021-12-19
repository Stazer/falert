const config = {
    mode: 'jit',
    content: ['./falert/frontend/**/*.{html,js,svelte,ts}'],

    theme: {
        extend: {},
    },

    plugins: [
        require('daisyui'),
    ],
};

module.exports = config;
