<template>
  <div>
    <h2 class="text-2xl font-bold text-gray-800 mb-6">发电分析</h2>

    <!-- 筛选条件 -->
    <div class="bg-white rounded-xl p-4 mb-6 shadow-sm flex flex-wrap items-center gap-4">
      <div class="flex items-center space-x-2">
        <label class="text-sm text-gray-600">开始日期</label>
        <input v-model="startDate" type="date" class="px-3 py-2 border border-gray-300 rounded-lg text-sm outline-none focus:border-orange-400" />
      </div>
      <div class="flex items-center space-x-2">
        <label class="text-sm text-gray-600">结束日期</label>
        <input v-model="endDate" type="date" class="px-3 py-2 border border-gray-300 rounded-lg text-sm outline-none focus:border-orange-400" />
      </div>
      <div class="flex items-center space-x-2">
        <label class="text-sm text-gray-600">电站</label>
        <select v-model="selectedStationId" class="px-3 py-2 border border-gray-300 rounded-lg text-sm outline-none focus:border-orange-400">
          <option value="">全部电站</option>
          <option v-for="s in stations" :key="s.id" :value="s.id">{{ s.name }}</option>
        </select>
      </div>
      <button @click="fetchGeneration" class="px-4 py-2 bg-orange-500 text-white rounded-lg text-sm hover:bg-orange-600">查询</button>
    </div>

    <!-- 错误提示 -->
    <div v-if="errorMsg" class="bg-red-50 text-red-600 rounded-xl p-4 mb-6 text-sm">{{ errorMsg }}</div>

    <!-- 汇总卡片 -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-5 mb-6">
      <DataCard title="期间总发电量" :value="totalGeneration.toFixed(2)" unit="kWh" icon="pi pi-chart-line" color="orange" />
      <DataCard title="日均发电量" :value="avgGeneration.toFixed(2)" unit="kWh" icon="pi pi-chart-bar" color="blue" />
      <DataCard title="查询天数" :value="dayCount" unit="天" icon="pi pi-calendar" color="green" />
    </div>

    <!-- 发电量图表 -->
    <div class="bg-white rounded-xl p-6 shadow-sm">
      <h3 class="text-lg font-semibold text-gray-700 mb-4">发电量趋势</h3>
      <div class="h-96">
        <ClientOnly><VChart :option="chartOption" autoresize /></ClientOnly>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import VChart from "vue-echarts";
import { use } from "echarts/core";
import { BarChart, LineChart } from "echarts/charts";
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
} from "echarts/components";
import { CanvasRenderer } from "echarts/renderers";

use([BarChart, LineChart, TitleComponent, TooltipComponent, LegendComponent, GridComponent, CanvasRenderer]);

const api = useApi();
const stations = ref<any[]>([]);
const selectedStationId = ref("");
const errorMsg = ref("");
const loading = ref(false);

// Default date range: last 30 days
const endDate = ref(new Date().toISOString().slice(0, 10));
const startDate = ref((() => {
  const d = new Date();
  d.setDate(d.getDate() - 29);
  return d.toISOString().slice(0, 10);
})());

const generationData = ref<{ date: string; kwh: number }[]>([]);

const totalGeneration = computed(() => generationData.value.reduce((sum, d) => sum + d.kwh, 0));
const dayCount = computed(() => generationData.value.length);
const avgGeneration = computed(() => dayCount.value > 0 ? totalGeneration.value / dayCount.value : 0);

const chartOption = computed(() => {
  return {
    tooltip: { trigger: "axis", axisPointer: { type: "shadow" } },
    grid: { left: "3%", right: "4%", bottom: "3%", containLabel: true },
    xAxis: {
      type: "category",
      data: generationData.value.map((d) => d.date),
      axisLabel: { fontSize: 10, rotate: generationData.value.length > 15 ? 45 : 0 },
    },
    yAxis: {
      type: "value",
      name: "kWh",
      axisLabel: { fontSize: 10 },
    },
    series: [
      {
        type: "bar",
        data: generationData.value.map((d) => d.kwh),
        barWidth: "60%",
        itemStyle: {
          color: {
            type: "linear",
            x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: "#f97316" },
              { offset: 1, color: "#fdba74" },
            ],
          },
          borderRadius: [3, 3, 0, 0],
        },
      },
    ],
  };
});

function getDaysInRange(start: string, end: string): string[] {
  const days: string[] = [];
  const current = new Date(start);
  const last = new Date(end);
  while (current <= last) {
    days.push(current.toISOString().slice(0, 10));
    current.setDate(current.getDate() + 1);
  }
  return days;
}

async function fetchStations() {
  try {
    const res = await api.get<any>("/stations", { page: 1, page_size: 100 });
    stations.value = res.items || res || [];
  } catch (e: any) {
    console.error("获取电站列表失败", e);
  }
}

async function fetchGeneration() {
  try {
    loading.value = true;
    errorMsg.value = "";

    const days = getDaysInRange(startDate.value, endDate.value);
    const dayMap: Record<string, number> = {};
    days.forEach((d) => (dayMap[d] = 0));

    const targetStations = selectedStationId.value
      ? stations.value.filter((s) => s.id === Number(selectedStationId.value))
      : stations.value.slice(0, 10);

    const promises = targetStations.map(async (s: any) => {
      try {
        const daily = await api.get<any>(`/stations/${s.id}/daily`, {
          start_date: startDate.value,
          end_date: endDate.value,
        });
        const items = daily.items || daily || [];
        for (const item of items) {
          const dateKey = (item.date || "").slice(0, 10);
          if (dayMap[dateKey] !== undefined) {
            dayMap[dateKey] += item.generation_kwh || item.daily_generation || 0;
          }
        }
      } catch {
        // Skip station if data unavailable
      }
    });

    await Promise.all(promises);

    generationData.value = days.map((d) => ({
      date: d.slice(5), // MM-DD
      kwh: Math.round(dayMap[d] * 100) / 100,
    }));
  } catch (e: any) {
    console.error("获取发电数据失败", e);
    errorMsg.value = "获取发电数据失败，请稍后重试";
  } finally {
    loading.value = false;
  }
}

onMounted(async () => {
  await fetchStations();
  fetchGeneration();
});
</script>
