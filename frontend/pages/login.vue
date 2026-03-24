<template>
  <div>
    <NuxtLayout name="auth">
      <!-- Loading spinner while validating existing token -->
      <div v-if="checking" class="text-center text-gray-400">
        <i class="pi pi-spin pi-spinner text-3xl"></i>
        <p class="mt-3 text-sm">验证登录状态...</p>
      </div>
      <div v-else class="w-full max-w-md">
        <div class="bg-white rounded-2xl shadow-xl p-8">
          <!-- Logo -->
          <div class="text-center mb-8">
            <i class="pi pi-sun text-5xl text-orange-500 mb-4"></i>
            <h1 class="text-2xl font-bold text-gray-800">光伏电站监控平台</h1>
            <p class="text-gray-500 mt-2 text-sm">Photovoltaic Monitoring System</p>
          </div>

          <!-- 表单 -->
          <form @submit.prevent="handleLogin" class="space-y-5">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">用户名</label>
              <input
                v-model="form.username"
                type="text"
                placeholder="请输入用户名"
                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent outline-none transition"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">密码</label>
              <input
                v-model="form.password"
                type="password"
                placeholder="请输入密码"
                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent outline-none transition"
              />
            </div>

            <p v-if="error" class="text-red-500 text-sm">{{ error }}</p>

            <button
              type="submit"
              :disabled="loading"
              class="w-full py-3 bg-orange-500 hover:bg-orange-600 text-white rounded-lg font-medium transition disabled:opacity-50"
            >
              {{ loading ? '登录中...' : '登 录' }}
            </button>
          </form>

          <p class="text-center text-gray-400 text-xs mt-6">默认账号: admin / admin123</p>
        </div>
      </div>
    </NuxtLayout>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: false });

const { login, isLoggedIn, fetchUser } = useAuth();
const form = reactive({ username: "", password: "" });
const loading = ref(false);
const error = ref("");
const checking = ref(true);

// On mount, if token already exists and is valid, skip login page
onMounted(async () => {
  if (isLoggedIn.value) {
    try {
      const u = await fetchUser();
      if (u) {
        await navigateTo("/", { replace: true });
        return;
      }
    } catch {
      // token invalid — fall through to show login form
    }
  }
  checking.value = false;
});

async function handleLogin() {
  error.value = "";
  loading.value = true;
  try {
    await login(form.username, form.password);
    await navigateTo("/", { replace: true });
  } catch (e: any) {
    error.value = e?.data?.detail || "登录失败";
  } finally {
    loading.value = false;
  }
}
</script>
