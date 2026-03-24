import PrimeVue from "primevue/config";
import Aura from "@primevue/themes/aura";
import ToastService from "primevue/toastservice";
import ConfirmationService from "primevue/confirmationservice";

export default defineNuxtPlugin((nuxtApp) => {
  nuxtApp.vueApp.use(PrimeVue, {
    theme: {
      preset: Aura,
      options: {
        prefix: "p",
        darkModeSelector: ".dark",
      },
    },
  });
  nuxtApp.vueApp.use(ToastService);
  nuxtApp.vueApp.use(ConfirmationService);
});
