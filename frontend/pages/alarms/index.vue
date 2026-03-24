<template>
  <div>
    <h2 class="text-2xl font-bold text-gray-800 mb-6">告警中心</h2>

    <!-- 告警统计 -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-5 mb-6">
      <DataCard title="严重告警" :value="stats.critical" unit="条" icon="pi pi-exclamation-circle" color="red" />
      <DataCard title="一般告警" :value="stats.warning" unit="条" icon="pi pi-exclamation-triangle" color="orange" />
      <DataCard title="提示信息" :value="stats.info" unit="条" icon="pi pi-info-circle" color="blue" />
      <DataCard title="活跃总数" :value="stats.total_active" unit="条" icon="pi pi-bell" color="purple" />
    </div>

    <!-- 筛选 -->
    <div class="bg-white rounded-xl p-4 mb-6 shadow-sm flex items-center space-x-4">
      <select v-model="filterLevel" class="px-4 py-2 border border-gray-300 rounded-lg text-sm outline-none">
        <option value="">全部级别</option>
        <option value="critical">严重</option>
        <option value="warning">告警</option>
        <option value="info">提示</option>
      </select>
      <select v-model="filterStatus" class="px-4 py-2 border border-gray-300 rounded-lg text-sm outline-none">
        <option value="">全部状态</option>
        <option value="active">活跃</option>
        <option value="confirmed">已确认</option>
        <option value="recovered">已恢复</option>
      </select>
      <button @click="fetchAlarms" class="px-4 py-2 bg-orange-500 text-white rounded-lg text-sm hover:bg-orange-600">查询</button>
    </div>

    <!-- 列表 -->
    <div class="bg-white rounded-xl shadow-sm overflow-hidden">
      <table class="w-full text-sm">
        <thead class="bg-gray-50 text-gray-500">
          <tr>
            <th class="px-4 py-3 text-center">级别</th>
            <th class="px-4 py-3 text-left">告警名称</th>
            <th class="px-4 py-3 text-left">电站</th>
            <th class="px-4 py-3 text-left">设备</th>
            <th class="px-4 py-3 text-left">告警时间</th>
            <th class="px-4 py-3 text-center">状态</th>
            <th class="px-4 py-3 text-center">操作</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr v-for="a in alarms" :key="a.id" class="hover:bg-gray-50">
            <td class="px-4 py-3 text-center">
              <i class="pi"
                :class="a.alarm_level === 'critical' ? 'pi-exclamation-circle text-red-500' : a.alarm_level === 'warning' ? 'pi-exclamation-triangle text-orange-500' : 'pi-info-circle text-blue-500'"
              ></i>
            </td>
            <td class="px-4 py-3 font-medium text-gray-800">{{ a.alarm_name }}</td>
            <td class="px-4 py-3 text-gray-500">{{ a.station_name }}</td>
            <td class="px-4 py-3 text-gray-500">{{ a.device_name || '-' }}</td>
            <td class="px-4 py-3 text-gray-500 text-xs">{{ a.alarm_time }}</td>
            <td class="px-4 py-3 text-center">
              <span class="px-2 py-1 text-xs rounded-full"
                :class="a.status === 'active' ? 'bg-red-100 text-red-700' : a.status === 'confirmed' ? 'bg-yellow-100 text-yellow-700' : 'bg-green-100 text-green-700'">
                {{ a.status === 'active' ? '活跃' : a.status === 'confirmed' ? '已确认' : '已恢复' }}
              </span>
            </td>
            <td class="px-4 py-3 text-center">
              <button v-if="a.status === 'active'" @click="confirmAlarm(a.id)" class="text-orange-500 hover:text-orange-700 text-xs">确认</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
const api = useApi();
const alarms = ref<any[]>([]);
const stats = ref({ critical: 0, warning: 0, info: 0, total_active: 0 });
const filterLevel = ref("");
const filterStatus = ref("");

async function fetchAlarms() {
  const params: any = { page: 1, page_size: 100 };
  if (filterLevel.value) params.alarm_level = filterLevel.value;
  if (filterStatus.value) params.status = filterStatus.value;
  const res = await api.get("/alarms", params);
  alarms.value = res.items || [];
}

async function fetchStats() {
  stats.value = await api.get("/alarms/stats");
}

async function confirmAlarm(id: number) {
  await api.post(`/alarms/${id}/confirm`);
  fetchAlarms();
  fetchStats();
}

onMounted(() => {
  fetchAlarms();
  fetchStats();
});
</script>
