<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-2xl font-bold text-gray-800">电站管理</h2>
      <div class="flex items-center space-x-3">
        <!-- 视图切换 -->
        <div class="flex bg-white rounded-lg border border-gray-200">
          <button
            v-for="v in views" :key="v.value"
            @click="viewMode = v.value"
            class="px-3 py-2 text-sm transition-colors"
            :class="viewMode === v.value ? 'bg-orange-500 text-white rounded-lg' : 'text-gray-600 hover:text-orange-500'"
          >
            <i :class="v.icon" class="mr-1"></i>{{ v.label }}
          </button>
        </div>
      </div>
    </div>

    <!-- 筛选栏 -->
    <div class="bg-white rounded-xl p-4 mb-6 shadow-sm flex items-center space-x-4">
      <input
        v-model="keyword"
        placeholder="搜索电站名称..."
        class="px-4 py-2 border border-gray-300 rounded-lg text-sm w-64 outline-none focus:ring-2 focus:ring-orange-500"
      />
      <select v-model="filterStatus" class="px-4 py-2 border border-gray-300 rounded-lg text-sm outline-none">
        <option value="">全部状态</option>
        <option value="normal">正常</option>
        <option value="fault">故障</option>
        <option value="offline">离线</option>
      </select>
      <button @click="fetchStations" class="px-4 py-2 bg-orange-500 text-white rounded-lg text-sm hover:bg-orange-600">
        查询
      </button>
    </div>

    <!-- 卡片视图 -->
    <div v-if="viewMode === 'card'" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
      <NuxtLink
        v-for="s in stations"
        :key="s.id"
        :to="`/stations/${s.id}`"
        class="bg-white rounded-xl p-5 shadow-sm hover:shadow-md transition-shadow cursor-pointer"
      >
        <div class="flex items-center justify-between mb-3">
          <h3 class="font-semibold text-gray-800 truncate">{{ s.name }}</h3>
          <span
            class="px-2 py-1 text-xs rounded-full"
            :class="statusClass(s.status)"
          >
            {{ statusLabel(s.status) }}
          </span>
        </div>
        <p class="text-xs text-gray-400 mb-3">{{ s.manufacturer_name }} · {{ s.capacity_kwp || '-' }} kWp</p>
        <div class="grid grid-cols-2 gap-3 text-sm">
          <div>
            <p class="text-gray-400 text-xs">实时功率</p>
            <p class="font-semibold text-blue-600">{{ s.current_power_kw ?? '-' }} kW</p>
          </div>
          <div>
            <p class="text-gray-400 text-xs">今日发电</p>
            <p class="font-semibold text-green-600">{{ s.today_generation ?? '-' }} kWh</p>
          </div>
        </div>
      </NuxtLink>
    </div>

    <!-- 表格视图 -->
    <div v-else-if="viewMode === 'table'" class="bg-white rounded-xl shadow-sm overflow-hidden">
      <table class="w-full text-sm">
        <thead class="bg-gray-50 text-gray-500">
          <tr>
            <th class="px-4 py-3 text-left">电站名称</th>
            <th class="px-4 py-3 text-left">厂家</th>
            <th class="px-4 py-3 text-right">装机容量</th>
            <th class="px-4 py-3 text-right">实时功率</th>
            <th class="px-4 py-3 text-right">今日发电</th>
            <th class="px-4 py-3 text-center">状态</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr v-for="s in stations" :key="s.id" class="hover:bg-gray-50 cursor-pointer" @click="navigateTo(`/stations/${s.id}`)">
            <td class="px-4 py-3 font-medium text-gray-800">{{ s.name }}</td>
            <td class="px-4 py-3 text-gray-500">{{ s.manufacturer_name }}</td>
            <td class="px-4 py-3 text-right">{{ s.capacity_kwp ?? '-' }} kWp</td>
            <td class="px-4 py-3 text-right text-blue-600">{{ s.current_power_kw ?? '-' }} kW</td>
            <td class="px-4 py-3 text-right text-green-600">{{ s.today_generation ?? '-' }} kWh</td>
            <td class="px-4 py-3 text-center">
              <span class="px-2 py-1 text-xs rounded-full" :class="statusClass(s.status)">{{ statusLabel(s.status) }}</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 地图视图占位 -->
    <div v-else class="bg-white rounded-xl p-6 shadow-sm h-96 flex items-center justify-center text-gray-400">
      <p>高德地图 — 电站分布（接入后显示）</p>
    </div>
  </div>
</template>

<script setup lang="ts">
const api = useApi();

const viewMode = ref("card");
const keyword = ref("");
const filterStatus = ref("");
const stations = ref<any[]>([]);

const views = [
  { value: "card", label: "卡片", icon: "pi pi-th-large" },
  { value: "table", label: "表格", icon: "pi pi-list" },
  { value: "map", label: "地图", icon: "pi pi-map" },
];

function statusClass(s: string) {
  return {
    normal: "bg-green-100 text-green-700",
    fault: "bg-red-100 text-red-700",
    offline: "bg-gray-100 text-gray-600",
    warning: "bg-yellow-100 text-yellow-700",
  }[s] || "bg-gray-100 text-gray-600";
}

function statusLabel(s: string) {
  return { normal: "正常", fault: "故障", offline: "离线", warning: "告警" }[s] || s;
}

async function fetchStations() {
  try {
    const params: any = { page: 1, page_size: 100 };
    if (keyword.value) params.keyword = keyword.value;
    if (filterStatus.value) params.status = filterStatus.value;
    const res = await api.get("/stations", params);
    stations.value = res.items || [];
  } catch (e) {
    console.error("获取电站列表失败", e);
  }
}

onMounted(fetchStations);
</script>
