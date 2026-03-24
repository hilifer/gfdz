<template>
  <div v-if="station">
    <!-- 头部 -->
    <div class="flex items-center justify-between mb-6">
      <div class="flex items-center space-x-3">
        <NuxtLink to="/stations" class="text-gray-400 hover:text-gray-600">
          <i class="pi pi-arrow-left text-lg"></i>
        </NuxtLink>
        <h2 class="text-2xl font-bold text-gray-800">{{ station.name }}</h2>
        <span class="px-2 py-1 text-xs rounded-full" :class="statusClass(station.status)">
          {{ statusLabel(station.status) }}
        </span>
      </div>
    </div>

    <!-- 实时数据卡片 -->
    <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-6">
      <DataCard title="实时功率" :value="station.realtime?.current_power_kw ?? '-'" unit="kW" icon="pi pi-gauge" color="blue" />
      <DataCard title="今日发电" :value="station.realtime?.today_generation ?? '-'" unit="kWh" icon="pi pi-sun" color="orange" />
      <DataCard title="本月发电" :value="station.realtime?.month_generation ?? '-'" unit="kWh" icon="pi pi-calendar" color="green" />
      <DataCard title="本年发电" :value="station.realtime?.year_generation ?? '-'" unit="kWh" icon="pi pi-chart-bar" color="purple" />
      <DataCard title="累计发电" :value="station.realtime?.total_generation ?? '-'" unit="kWh" icon="pi pi-database" color="cyan" />
      <DataCard title="今日收益" :value="station.realtime?.today_revenue ?? '-'" unit="元" icon="pi pi-dollar" color="green" />
    </div>

    <!-- 基本信息 + 图表 -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
      <!-- 基本信息 -->
      <div class="bg-white rounded-xl p-6 shadow-sm">
        <h3 class="text-lg font-semibold text-gray-700 mb-4">基本信息</h3>
        <dl class="space-y-3 text-sm">
          <div class="flex justify-between">
            <dt class="text-gray-500">装机容量</dt>
            <dd class="text-gray-800 font-medium">{{ station.capacity_kwp ?? '-' }} kWp</dd>
          </div>
          <div class="flex justify-between">
            <dt class="text-gray-500">地址</dt>
            <dd class="text-gray-800">{{ station.address || '-' }}</dd>
          </div>
          <div class="flex justify-between">
            <dt class="text-gray-500">电站类型</dt>
            <dd class="text-gray-800">{{ station.station_type || '-' }}</dd>
          </div>
          <div class="flex justify-between">
            <dt class="text-gray-500">并网日期</dt>
            <dd class="text-gray-800">{{ station.commissioned_date || '-' }}</dd>
          </div>
          <div class="flex justify-between">
            <dt class="text-gray-500">电价</dt>
            <dd class="text-gray-800">{{ station.electricity_price ?? '-' }} 元/kWh</dd>
          </div>
          <div class="flex justify-between">
            <dt class="text-gray-500">联系人</dt>
            <dd class="text-gray-800">{{ station.contact_name || '-' }}</dd>
          </div>
          <div class="flex justify-between">
            <dt class="text-gray-500">设备数量</dt>
            <dd class="text-gray-800">{{ station.device_count ?? 0 }} 台</dd>
          </div>
        </dl>
      </div>

      <!-- 功率曲线占位 -->
      <div class="bg-white rounded-xl p-6 shadow-sm lg:col-span-2">
        <h3 class="text-lg font-semibold text-gray-700 mb-4">今日功率曲线</h3>
        <div class="h-64 flex items-center justify-center text-gray-400">
          <p>ECharts 功率曲线图</p>
        </div>
      </div>
    </div>

    <!-- 发电量柱状图 -->
    <div class="bg-white rounded-xl p-6 shadow-sm">
      <h3 class="text-lg font-semibold text-gray-700 mb-4">近30天发电量</h3>
      <div class="h-72 flex items-center justify-center text-gray-400">
        <p>ECharts 柱状图 — 每日发电量</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const route = useRoute();
const api = useApi();
const station = ref<any>(null);

function statusClass(s: string) {
  return {
    normal: "bg-green-100 text-green-700",
    fault: "bg-red-100 text-red-700",
    offline: "bg-gray-100 text-gray-600",
  }[s] || "bg-gray-100 text-gray-600";
}

function statusLabel(s: string) {
  return { normal: "正常", fault: "故障", offline: "离线" }[s] || s;
}

onMounted(async () => {
  try {
    station.value = await api.get(`/stations/${route.params.id}`);
  } catch (e) {
    console.error("获取电站详情失败", e);
  }
});
</script>
