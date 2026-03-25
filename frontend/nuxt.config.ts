import Aura from "@primevue/themes/aura";

export default defineNuxtConfig({
  devtools: { enabled: false },

  modules: ["@pinia/nuxt", "@nuxtjs/tailwindcss"],

  css: ["primeicons/primeicons.css", "~/assets/css/main.css"],

  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || "/api",
    },
  },

  // PrimeVue 手动注册（通过 plugin）
  build: {
    transpile: ["primevue", "echarts", "vue-echarts"],
  },

  compatibilityDate: "2025-01-01",
});
