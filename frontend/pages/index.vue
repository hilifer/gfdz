<template>
  <div>
    <h2 class="text-2xl font-bold text-gray-800 mb-6">总览大屏</h2>

    <!-- 数据卡片 -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5 mb-6">
      <DataCard title="电站总数" :value="summary.station_count" unit="座" icon="pi pi-building" color="blue" />
      <DataCard title="总装机容量" :value="formatNum(summary.total_capacity_kwp)" unit="kWp" icon="pi pi-bolt" color="orange" />
      <DataCard title="今日发电" :value="formatNum(summary.today_generation_kwh)" unit="kWh" icon="pi pi-chart-line" color="green" />
      <DataCard title="实时总功率" :value="formatNum(summary.current_power_kw)" unit="kW" icon="pi pi-gauge" color="purple" />
    </div>

    <!-- 第二行 -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5 mb-6">
      <DataCard title="累计发电" :value="formatNum(summary.total_generation_kwh)" unit="kWh" icon="pi pi-database" color="cyan" />
      <DataCard
        title="活跃告警"
        :value="summary.active_alarms"
        unit="条"
        icon="pi pi-exclamation-triangle"
        :color="summary.active_alarms > 0 ? 'red' : 'green'"
      />
      <DataCard title="正常电站" :value="summary.status_distribution?.normal || 0" unit="座" icon="pi pi-check-circle" color="green" />
      <DataCard title="故障电站" :value="(summary.status_distribution?.fault || 0) + (summary.status_distribution?.offline || 0)" unit="座" icon="pi pi-times-circle" color="red" />
    </div>

    <!-- 图表区域 -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div class="bg-white rounded-xl p-6 shadow-sm">
        <h3 class="text-lg font-semibold text-gray-700 mb-4">电站状态分布</h3>
        <div class="h-72 flex items-center justify-center text-gray-400">
          <p>ECharts 饼图 — 正常/告警/故障/离线</p>
        </div>
      </div>
      <div class="bg-white rounded-xl p-6 shadow-sm">
        <h3 class="text-lg font-semibold text-gray-700 mb-4">近7天发电趋势</h3>
        <div class="h-72 flex items-center justify-center text-gray-400">
          <p>ECharts 柱状图 — 每日发电量</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const api = useApi();

const summary = ref<any>({
  station_count: 0,
  total_capacity_kwp: 0,
  today_generation_kwh: 0,
  current_power_kw: 0,
  total_generation_kwh: 0,
  active_alarms: 0,
  status_distribution: {},
});

function formatNum(val: number | undefined) {
  if (!val) return "0";
  if (val >= 10000) return (val / 10000).toFixed(2) + "万";
  return val.toFixed(2);
}

onMounted(async () => {
  try {
    summary.value = await api.get("/dashboard/summary");
  } catch (e) {
    console.error("获取总览数据失败", e);
  }
});
</script>
