<template>
  <div v-if="device">
    <div class="flex items-center space-x-3 mb-6">
      <NuxtLink to="/devices" class="text-gray-400 hover:text-gray-600">
        <i class="pi pi-arrow-left text-lg"></i>
      </NuxtLink>
      <h2 class="text-2xl font-bold text-gray-800">{{ device.device_name }}</h2>
      <span class="text-sm text-gray-500">{{ device.device_code }}</span>
    </div>

    <!-- 实时数据 -->
    <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-6">
      <DataCard title="功率" :value="device.latest_data?.power_kw ?? '-'" unit="kW" icon="pi pi-gauge" color="blue" />
      <DataCard title="电压" :value="device.latest_data?.voltage_v ?? '-'" unit="V" icon="pi pi-bolt" color="orange" />
      <DataCard title="电流" :value="device.latest_data?.current_a ?? '-'" unit="A" icon="pi pi-wave-pulse" color="green" />
      <DataCard title="温度" :value="device.latest_data?.temperature ?? '-'" unit="℃" icon="pi pi-sun" color="red" />
      <DataCard title="日发电量" :value="device.latest_data?.daily_generation ?? '-'" unit="kWh" icon="pi pi-chart-line" color="cyan" />
      <DataCard title="额定功率" :value="device.rated_power ?? '-'" unit="kW" icon="pi pi-info-circle" color="purple" />
    </div>

    <!-- 历史曲线 -->
    <div class="bg-white rounded-xl p-6 shadow-sm">
      <h3 class="text-lg font-semibold text-gray-700 mb-4">历史功率曲线</h3>
      <div class="h-80 flex items-center justify-center text-gray-400">
        <p>ECharts 功率/电压/电流 曲线图</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const route = useRoute();
const api = useApi();
const device = ref<any>(null);

onMounted(async () => {
  device.value = await api.get(`/devices/${route.params.id}`);
});
</script>
