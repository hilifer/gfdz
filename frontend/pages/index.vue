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
        <div class="h-72">
          <VChart :option="pieOption" autoresize />
        </div>
      </div>
      <div class="bg-white rounded-xl p-6 shadow-sm">
        <h3 class="text-lg font-semibold text-gray-700 mb-4">近7天发电趋势</h3>
        <div class="h-72">
          <VChart :option="barOption" autoresize />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import VChart from "vue-echarts";
import { use } from "echarts/core";
import { PieChart, BarChart } from "echarts/charts";
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
} from "echarts/components";
import { CanvasRenderer } from "echarts/renderers";

use([PieChart, BarChart, TitleComponent, TooltipComponent, LegendComponent, GridComponent, CanvasRenderer]);

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

const generationDays = ref<{ date: string; kwh: number }[]>([]);
const errorMsg = ref("");

function formatNum(val: number | undefined) {
  if (!val) return "0";
  if (val >= 10000) return (val / 10000).toFixed(2) + "万";
  return val.toFixed(2);
}

// Pie chart for station status distribution
const pieOption = computed(() => {
  const dist = summary.value.status_distribution || {};
  return {
    tooltip: { trigger: "item", formatter: "{b}: {c} ({d}%)" },
    legend: { bottom: 0 },
    series: [
      {
        type: "pie",
        radius: ["40%", "65%"],
        avoidLabelOverlap: true,
        itemStyle: { borderRadius: 6, borderColor: "#fff", borderWidth: 2 },
        label: { show: true, formatter: "{b}: {c}" },
        data: [
          { value: dist.normal || 0, name: "正常", itemStyle: { color: "#22c55e" } },
          { value: dist.fault || 0, name: "故障", itemStyle: { color: "#ef4444" } },
          { value: dist.offline || 0, name: "离线", itemStyle: { color: "#9ca3af" } },
        ],
      },
    ],
  };
});

// Bar chart for 7-day generation trend
const barOption = computed(() => {
  const dates = generationDays.value.map((d) => d.date);
  const values = generationDays.value.map((d) => d.kwh);
  return {
    tooltip: { trigger: "axis", axisPointer: { type: "shadow" } },
    grid: { left: "3%", right: "4%", bottom: "3%", containLabel: true },
    xAxis: {
      type: "category",
      data: dates,
      axisLabel: { fontSize: 11 },
    },
    yAxis: {
      type: "value",
      name: "kWh",
      axisLabel: { fontSize: 11 },
    },
    series: [
      {
        type: "bar",
        data: values,
        barWidth: "50%",
        itemStyle: {
          color: {
            type: "linear",
            x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: "#f97316" },
              { offset: 1, color: "#fdba74" },
            ],
          },
          borderRadius: [4, 4, 0, 0],
        },
      },
    ],
  };
});

// Generate last 7 days date strings
function getLast7Days(): string[] {
  const days: string[] = [];
  for (let i = 6; i >= 0; i--) {
    const d = new Date();
    d.setDate(d.getDate() - i);
    days.push(d.toISOString().slice(0, 10));
  }
  return days;
}

onMounted(async () => {
  // Fetch dashboard summary
  try {
    summary.value = await api.get("/dashboard/summary");
  } catch (e: any) {
    console.error("获取总览数据失败", e);
    errorMsg.value = "获取总览数据失败，请稍后重试";
  }

  // Fetch 7-day generation data from stations
  try {
    const days = getLast7Days();
    const res = await api.get<any>("/stations", { page: 1, page_size: 100 });
    const stations = res.items || res || [];

    // Build daily totals from station daily data
    const dayMap: Record<string, number> = {};
    days.forEach((d) => (dayMap[d] = 0));

    if (stations.length > 0) {
      // Try to get daily data for each station
      const promises = stations.slice(0, 10).map(async (s: any) => {
        try {
          const daily = await api.get<any>(`/stations/${s.id}/daily`, {
            start_date: days[0],
            end_date: days[days.length - 1],
          });
          const items = daily.items || daily || [];
          for (const item of items) {
            const dateKey = (item.date || "").slice(0, 10);
            if (dayMap[dateKey] !== undefined) {
              dayMap[dateKey] += item.generation_kwh || item.daily_generation || 0;
            }
          }
        } catch {
          // Skip station if daily data unavailable
        }
      });
      await Promise.all(promises);
    }

    generationDays.value = days.map((d) => ({
      date: d.slice(5), // MM-DD format
      kwh: Math.round(dayMap[d] * 100) / 100,
    }));
  } catch (e: any) {
    console.error("获取发电趋势失败", e);
    // Fallback: show empty chart
    const days = getLast7Days();
    generationDays.value = days.map((d) => ({ date: d.slice(5), kwh: 0 }));
  }
});
</script>
