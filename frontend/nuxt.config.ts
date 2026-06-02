// https://nuxt.com/docs/api/configuration/nuxt-config

export default defineNuxtConfig({
  vite: {
    optimizeDeps: {
      include: [
        '@vue/devtools-core',
        '@vue/devtools-kit',
      ]
    }
  }
})
