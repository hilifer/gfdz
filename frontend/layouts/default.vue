<template>
  <div class="flex h-screen bg-gray-50">
    <!-- 侧边栏 -->
    <aside class="w-64 bg-white border-r border-gray-200 flex flex-col">
      <!-- Logo -->
      <div class="h-16 flex items-center px-6 border-b border-gray-200">
        <i class="pi pi-sun text-2xl text-orange-500 mr-3"></i>
        <span class="text-lg font-bold text-gray-800">光伏监控平台</span>
      </div>

      <!-- 导航菜单 -->
      <nav class="flex-1 py-4 overflow-y-auto">
        <ul class="space-y-1 px-3">
          <li v-for="item in menuItems" :key="item.path">
            <NuxtLink
              :to="item.path"
              class="flex items-center px-3 py-2.5 rounded-lg text-sm transition-colors"
              :class="isActive(item.path)
                ? 'bg-orange-50 text-orange-600 font-medium'
                : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'"
            >
              <i :class="item.icon" class="text-lg mr-3 w-5 text-center"></i>
              {{ item.label }}
            </NuxtLink>
          </li>
        </ul>

        <!-- 系统管理分组 -->
        <div class="mt-6 pt-4 border-t border-gray-200 px-3">
          <p class="px-3 mb-2 text-xs font-semibold text-gray-400 uppercase">系统管理</p>
          <ul class="space-y-1">
            <li v-for="item in settingsItems" :key="item.path">
              <NuxtLink
                :to="item.path"
                class="flex items-center px-3 py-2.5 rounded-lg text-sm transition-colors"
                :class="isActive(item.path)
                  ? 'bg-orange-50 text-orange-600 font-medium'
                  : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'"
              >
                <i :class="item.icon" class="text-lg mr-3 w-5 text-center"></i>
                {{ item.label }}
              </NuxtLink>
            </li>
          </ul>
        </div>
      </nav>
    </aside>

    <!-- 主内容区 -->
    <div class="flex-1 flex flex-col overflow-hidden">
      <!-- 顶栏 -->
      <header class="h-16 bg-white border-b border-gray-200 flex items-center justify-between px-6">
        <div class="text-gray-500 text-sm">
          {{ currentTime }}
        </div>
        <div class="flex items-center space-x-4">
          <!-- 告警提示 -->
          <NuxtLink to="/alarms" class="relative">
            <i class="pi pi-bell text-xl text-gray-500 hover:text-orange-500 transition-colors"></i>
            <span v-if="alarmCount > 0"
              class="absolute -top-1 -right-2 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
              {{ alarmCount > 99 ? '99+' : alarmCount }}
            </span>
          </NuxtLink>

          <!-- 用户 -->
          <div class="flex items-center space-x-2 cursor-pointer" @click="handleLogout">
            <i class="pi pi-user text-gray-500"></i>
            <span class="text-sm text-gray-700">{{ user?.display_name || '管理员' }}</span>
            <i class="pi pi-sign-out text-gray-400 text-sm"></i>
          </div>
        </div>
      </header>

      <!-- 页面内容 -->
      <main class="flex-1 overflow-y-auto p-6">
        <slot />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
const route = useRoute();
const api = useApi();
const { user, logout, fetchUser, isLoggedIn } = useAuth();

const alarmCount = ref(0);
const currentTime = ref("");

let timeTimer: ReturnType<typeof setInterval> | null = null;
let alarmTimer: ReturnType<typeof setInterval> | null = null;

const menuItems = [
  { path: "/", label: "总览大屏", icon: "pi pi-chart-bar" },
  { path: "/stations", label: "电站管理", icon: "pi pi-building" },
  { path: "/devices", label: "设备管理", icon: "pi pi-server" },
  { path: "/alarms", label: "告警中心", icon: "pi pi-exclamation-triangle" },
  { path: "/analysis/generation", label: "发电分析", icon: "pi pi-chart-line" },
  { path: "/analysis/revenue", label: "收益分析", icon: "pi pi-dollar" },
  { path: "/work-orders", label: "工单管理", icon: "pi pi-clipboard" },
];

const settingsItems = [
  { path: "/settings/manufacturers", label: "厂家管理", icon: "pi pi-cog" },
  { path: "/settings/price", label: "电价配置", icon: "pi pi-money-bill" },
  { path: "/settings/users", label: "用户管理", icon: "pi pi-users" },
];

function isActive(path: string) {
  if (path === "/") return route.path === "/";
  return route.path.startsWith(path);
}

function handleLogout() {
  logout();
}

async function fetchAlarmCount() {
  try {
    const stats = await api.get<any>("/alarms/stats");
    alarmCount.value = stats.total_active ?? 0;
  } catch (e) {
    console.error("获取告警数量失败", e);
  }
}

// 时间更新 + 告警轮询
onMounted(() => {
  const update = () => {
    const now = new Date();
    currentTime.value = now.toLocaleString("zh-CN", {
      year: "numeric", month: "2-digit", day: "2-digit",
      hour: "2-digit", minute: "2-digit", second: "2-digit",
    });
  };
  update();
  timeTimer = setInterval(update, 1000);

  // Fetch alarm count immediately, then every 60 seconds
  fetchAlarmCount();
  alarmTimer = setInterval(fetchAlarmCount, 60000);
});

onUnmounted(() => {
  if (timeTimer) clearInterval(timeTimer);
  if (alarmTimer) clearInterval(alarmTimer);
});
</script>
