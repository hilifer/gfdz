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

  // Nuxt 直接代理 /api 到后端，不需要 nginx
  nitro: {
    devProxy: {
      "/api": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
      },
    },
    routeRules: {
      "/api/**": {
        proxy: "http://127.0.0.1:8000/api/**",
      },
    },
  },

  // PrimeVue 手动注册（通过 plugin）
  build: {
    transpile: ["primevue", "echarts", "vue-echarts"],
  },

  vite: {
    server: {
      hmr: {
        protocol: "ws",
        clientPort: 5001,
      },
    },
  },

  compatibilityDate: "2025-01-01",
});
