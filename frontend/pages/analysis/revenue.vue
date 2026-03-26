<template>
  <div>
    <h2 class="text-2xl font-bold text-gray-800 mb-6">收益分析</h2>

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
      <button @click="fetchRevenue" class="px-4 py-2 bg-orange-500 text-white rounded-lg text-sm hover:bg-orange-600">查询</button>
    </div>

    <!-- 平台限制提示 -->
    <div v-if="dateRangeWarning" class="bg-yellow-50 text-yellow-700 rounded-xl p-3 mb-4 text-sm flex items-center gap-2">
      <i class="pi pi-exclamation-triangle"></i>
      {{ dateRangeWarning }}
    </div>

    <!-- 错误提示 -->
    <div v-if="errorMsg" class="bg-red-50 text-red-600 rounded-xl p-4 mb-6 text-sm">{{ errorMsg }}</div>

    <!-- 汇总卡片 -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-5 mb-6">
      <DataCard title="期间总收益" :value="totalRevenue.toFixed(2)" unit="元" icon="pi pi-dollar" color="green" />
      <DataCard title="期间总发电量" :value="totalGeneration.toFixed(2)" unit="kWh" icon="pi pi-chart-line" color="orange" />
      <DataCard title="日均收益" :value="avgRevenue.toFixed(2)" unit="元" icon="pi pi-chart-bar" color="blue" />
      <DataCard title="电站数量" :value="stationRevenues.length" unit="座" icon="pi pi-building" color="purple" />
    </div>

    <!-- 各电站收益明细 -->
    <div class="bg-white rounded-xl shadow-sm overflow-hidden mb-6">
      <div class="px-6 py-4 border-b border-gray-100">
        <h3 class="text-lg font-semibold text-gray-700">各电站收益明细</h3>
      </div>
      <table class="w-full text-sm">
        <thead class="bg-gray-50 text-gray-500">
          <tr>
            <th class="px-4 py-3 text-left">电站名称</th>
            <th class="px-4 py-3 text-right">装机容量(kWp)</th>
            <th class="px-4 py-3 text-right">电价(元/kWh)</th>
            <th class="px-4 py-3 text-right">期间发电量(kWh)</th>
            <th class="px-4 py-3 text-right">预估收益(元)</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr v-for="s in stationRevenues" :key="s.id" class="hover:bg-gray-50">
            <td class="px-4 py-3 font-medium text-gray-800">{{ s.name }}</td>
            <td class="px-4 py-3 text-right text-gray-500">{{ s.capacity_kwp ?? '-' }}</td>
            <td class="px-4 py-3 text-right text-gray-500">{{ s.electricity_price ?? '未设置' }}</td>
            <td class="px-4 py-3 text-right text-gray-800">{{ s.generation.toFixed(2) }}</td>
            <td class="px-4 py-3 text-right font-medium text-green-600">{{ s.revenue.toFixed(2) }}</td>
          </tr>
          <tr v-if="stationRevenues.length === 0">
            <td colspan="5" class="px-4 py-8 text-center text-gray-400">暂无数据，请点击查询</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 收益趋势图 -->
    <div class="bg-white rounded-xl p-6 shadow-sm">
      <h3 class="text-lg font-semibold text-gray-700 mb-4">收益趋势</h3>
      <div class="h-80">
        <ClientOnly><VChart :option="chartOption" autoresize /></ClientOnly>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import VChart from "vue-echarts";
import { use } from "echarts/core";
import { BarChart } from "echarts/charts";
import {
  TitleComponent,
  TooltipComponent,
  GridComponent,
  LegendComponent,
} from "echarts/components";
import { CanvasRenderer } from "echarts/renderers";

use([BarChart, TitleComponent, TooltipComponent, GridComponent, LegendComponent, CanvasRenderer]);

const api = useApi();
const errorMsg = ref("");

const endDate = ref(new Date().toISOString().slice(0, 10));
const startDate = ref((() => {
  const d = new Date();
  d.setDate(d.getDate() - 29);
  return d.toISOString().slice(0, 10);
})());

const stationRevenues = ref<any[]>([]);
const dailyRevenue = ref<{ date: string; revenue: number }[]>([]);

const dateRangeWarning = computed(() => {
  const s = new Date(startDate.value);
  const e = new Date(endDate.value);
  const days = Math.ceil((e.getTime() - s.getTime()) / 86400000);
  if (days > 100) return `查询跨度${days}天超出平台限制(爱士惟≤7天 锦浪≤31天 阳光≤100天)，数据将自动截断`;
  if (days > 31) return `查询跨度${days}天，爱士惟(≤7天)和锦浪(≤31天)电站数据可能不完整`;
  if (days > 7) return `查询跨度${days}天，爱士惟平台电站数据可能不完整(限制≤7天)`;
  return "";
});

const totalGeneration = computed(() => stationRevenues.value.reduce((sum, s) => sum + s.generation, 0));
const totalRevenue = computed(() => stationRevenues.value.reduce((sum, s) => sum + s.revenue, 0));
const avgRevenue = computed(() => {
  const days = dailyRevenue.value.length;
  return days > 0 ? totalRevenue.value / days : 0;
});

const chartOption = computed(() => {
  return {
    tooltip: { trigger: "axis", axisPointer: { type: "shadow" } },
    grid: { left: "3%", right: "4%", bottom: "3%", containLabel: true },
    xAxis: {
      type: "category",
      data: dailyRevenue.value.map((d) => d.date),
      axisLabel: { fontSize: 10, rotate: dailyRevenue.value.length > 15 ? 45 : 0 },
    },
    yAxis: {
      type: "value",
      name: "元",
      axisLabel: { fontSize: 10 },
    },
    series: [
      {
        type: "bar",
        data: dailyRevenue.value.map((d) => d.revenue),
        barWidth: "60%",
        itemStyle: {
          color: {
            type: "linear",
            x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: "#22c55e" },
              { offset: 1, color: "#86efac" },
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

async function fetchRevenue() {
  try {
    errorMsg.value = "";

    // Get stations with prices
    const stationsRes = await api.get<any>("/stations", { page: 1, page_size: 100 });
    const stations = stationsRes.items || stationsRes || [];

    const days = getDaysInRange(startDate.value, endDate.value);
    const dayMap: Record<string, number> = {};
    days.forEach((d) => (dayMap[d] = 0));

    const results: any[] = [];

    const promises = stations.slice(0, 20).map(async (s: any) => {
      try {
        const daily = await api.get<any>(`/stations/${s.id}/daily`, {
          start_date: startDate.value,
          end_date: endDate.value,
        });
        const items = daily.items || daily || [];
        let stationGen = 0;
        for (const item of items) {
          const gen = item.generation_kwh || item.daily_generation || 0;
          stationGen += gen;
          const dateKey = (item.date || "").slice(0, 10);
          if (dayMap[dateKey] !== undefined) {
            dayMap[dateKey] += gen * (s.electricity_price || 0);
          }
        }
        const price = s.electricity_price || 0;
        results.push({
          id: s.id,
          name: s.name,
          capacity_kwp: s.capacity_kwp,
          electricity_price: price,
          generation: stationGen,
          revenue: stationGen * price,
        });
      } catch {
        results.push({
          id: s.id,
          name: s.name,
          capacity_kwp: s.capacity_kwp,
          electricity_price: s.electricity_price || 0,
          generation: 0,
          revenue: 0,
        });
      }
    });

    await Promise.all(promises);
    stationRevenues.value = results.sort((a, b) => b.revenue - a.revenue);
    dailyRevenue.value = days.map((d) => ({
      date: d.slice(5),
      revenue: Math.round(dayMap[d] * 100) / 100,
    }));
  } catch (e: any) {
    console.error("获取收益数据失败", e);
    errorMsg.value = "获取收益数据失败，请稍后重试";
  }
}

onMounted(fetchRevenue);
</script>
