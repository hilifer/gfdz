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

    <!-- 基本信息 + 功率曲线 -->
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

      <!-- 今日功率曲线 -->
      <div class="bg-white rounded-xl p-6 shadow-sm lg:col-span-2">
        <h3 class="text-lg font-semibold text-gray-700 mb-4">今日功率曲线</h3>
        <div class="h-64">
          <ClientOnly><VChart :option="powerCurveOption" autoresize /></ClientOnly>
        </div>
      </div>
    </div>

    <!-- 30天发电量柱状图 -->
    <div class="bg-white rounded-xl p-6 shadow-sm">
      <h3 class="text-lg font-semibold text-gray-700 mb-4">近30天发电量</h3>
      <div class="h-72">
        <ClientOnly><VChart :option="generationBarOption" autoresize /></ClientOnly>
      </div>
    </div>
  </div>
  <div v-else class="flex items-center justify-center h-64">
    <p class="text-gray-400">{{ errorMsg || '加载中...' }}</p>
  </div>
</template>

<script setup lang="ts">
import VChart from "vue-echarts";
import { use } from "echarts/core";
import { LineChart, BarChart } from "echarts/charts";
import {
  TitleComponent,
  TooltipComponent,
  GridComponent,
} from "echarts/components";
import { CanvasRenderer } from "echarts/renderers";

use([LineChart, BarChart, TitleComponent, TooltipComponent, GridComponent, CanvasRenderer]);

const route = useRoute();
const api = useApi();
const station = ref<any>(null);
const errorMsg = ref("");

const powerCurveData = ref<{ time: string; power: number }[]>([]);
const generationData = ref<{ date: string; kwh: number }[]>([]);

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

// Power curve chart option
const powerCurveOption = computed(() => {
  return {
    tooltip: { trigger: "axis" },
    grid: { left: "3%", right: "4%", bottom: "3%", containLabel: true },
    xAxis: {
      type: "category",
      data: powerCurveData.value.map((d) => d.time),
      axisLabel: { fontSize: 10 },
      boundaryGap: false,
    },
    yAxis: {
      type: "value",
      name: "kW",
      axisLabel: { fontSize: 10 },
    },
    series: [
      {
        type: "line",
        data: powerCurveData.value.map((d) => d.power),
        smooth: true,
        symbol: "none",
        lineStyle: { color: "#3b82f6", width: 2 },
        areaStyle: {
          color: {
            type: "linear",
            x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: "rgba(59,130,246,0.3)" },
              { offset: 1, color: "rgba(59,130,246,0.02)" },
            ],
          },
        },
      },
    ],
  };
});

// 30-day generation bar chart option
const generationBarOption = computed(() => {
  return {
    tooltip: { trigger: "axis", axisPointer: { type: "shadow" } },
    grid: { left: "3%", right: "4%", bottom: "3%", containLabel: true },
    xAxis: {
      type: "category",
      data: generationData.value.map((d) => d.date),
      axisLabel: { fontSize: 10, rotate: 45 },
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

function getLast30Days(): string[] {
  const days: string[] = [];
  for (let i = 29; i >= 0; i--) {
    const d = new Date();
    d.setDate(d.getDate() - i);
    days.push(d.toISOString().slice(0, 10));
  }
  return days;
}

onMounted(async () => {
  const stationId = route.params.id;

  // Fetch station details
  try {
    station.value = await api.get(`/stations/${stationId}`);
  } catch (e: any) {
    console.error("获取电站详情失败", e);
    errorMsg.value = "获取电站详情失败，请返回重试";
    return;
  }

  // Fetch today's power curve
  try {
    const today = new Date().toISOString().slice(0, 10);
    const daily = await api.get<any>(`/stations/${stationId}/daily`, {
      start_date: today,
      end_date: today,
    });
    const items = daily.items || daily || [];
    // Parse time-series power data
    if (items.length > 0 && items[0].power_curve) {
      // If API returns power_curve array
      powerCurveData.value = items[0].power_curve.map((p: any) => ({
        time: p.time || p.timestamp || "",
        power: p.power_kw || p.power || 0,
      }));
    } else {
      // Each item may represent a time point
      powerCurveData.value = items.map((item: any) => ({
        time: (item.timestamp || item.time || item.date || "").slice(11, 16) || item.hour || "",
        power: item.power_kw || item.current_power_kw || 0,
      }));
    }
  } catch (e: any) {
    console.error("获取功率曲线失败", e);
  }

  // Fetch 30-day generation data
  try {
    const days = getLast30Days();
    const daily = await api.get<any>(`/stations/${stationId}/daily`, {
      start_date: days[0],
      end_date: days[days.length - 1],
    });
    const items = daily.items || daily || [];
    const dayMap: Record<string, number> = {};
    days.forEach((d) => (dayMap[d] = 0));
    for (const item of items) {
      const dateKey = (item.date || "").slice(0, 10);
      if (dayMap[dateKey] !== undefined) {
        dayMap[dateKey] = item.generation_kwh || item.daily_generation || 0;
      }
    }
    generationData.value = days.map((d) => ({
      date: d.slice(5), // MM-DD
      kwh: Math.round(dayMap[d] * 100) / 100,
    }));
  } catch (e: any) {
    console.error("获取30天发电数据失败", e);
    const days = getLast30Days();
    generationData.value = days.map((d) => ({ date: d.slice(5), kwh: 0 }));
  }
});
</script>
