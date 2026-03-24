<template>
  <div>
    <h2 class="text-2xl font-bold text-gray-800 mb-6">设备管理</h2>

    <!-- 筛选 -->
    <div class="bg-white rounded-xl p-4 mb-6 shadow-sm flex items-center space-x-4">
      <select v-model="filterType" class="px-4 py-2 border border-gray-300 rounded-lg text-sm outline-none">
        <option value="">全部类型</option>
        <option value="inverter">逆变器</option>
        <option value="meter">电表</option>
        <option value="combiner_box">汇流箱</option>
        <option value="weather_station">气象站</option>
        <option value="storage">储能</option>
      </select>
      <select v-model="filterStatus" class="px-4 py-2 border border-gray-300 rounded-lg text-sm outline-none">
        <option value="">全部状态</option>
        <option value="normal">正常</option>
        <option value="fault">故障</option>
        <option value="offline">离线</option>
      </select>
      <button @click="fetchDevices" class="px-4 py-2 bg-orange-500 text-white rounded-lg text-sm hover:bg-orange-600">查询</button>
    </div>

    <!-- 错误提示 -->
    <div v-if="errorMsg" class="bg-red-50 text-red-600 rounded-xl p-4 mb-6 text-sm">{{ errorMsg }}</div>

    <!-- 表格 -->
    <div class="bg-white rounded-xl shadow-sm overflow-hidden">
      <table class="w-full text-sm">
        <thead class="bg-gray-50 text-gray-500">
          <tr>
            <th class="px-4 py-3 text-left">设备名称</th>
            <th class="px-4 py-3 text-left">所属电站</th>
            <th class="px-4 py-3 text-left">类型</th>
            <th class="px-4 py-3 text-left">品牌/型号</th>
            <th class="px-4 py-3 text-right">额定功率</th>
            <th class="px-4 py-3 text-center">状态</th>
            <th class="px-4 py-3 text-left">最后更新</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr v-for="d in devices" :key="d.id" class="hover:bg-gray-50 cursor-pointer" @click="navigateTo(`/devices/${d.id}`)">
            <td class="px-4 py-3 font-medium text-gray-800">{{ d.device_name }}</td>
            <td class="px-4 py-3 text-gray-500">{{ d.station_name }}</td>
            <td class="px-4 py-3 text-gray-500">{{ typeLabel(d.device_type) }}</td>
            <td class="px-4 py-3 text-gray-500">{{ d.brand || '-' }} {{ d.model || '' }}</td>
            <td class="px-4 py-3 text-right">{{ d.rated_power ?? '-' }} kW</td>
            <td class="px-4 py-3 text-center">
              <span class="px-2 py-1 text-xs rounded-full"
                :class="d.status === 'normal' ? 'bg-green-100 text-green-700' : d.status === 'fault' ? 'bg-red-100 text-red-700' : 'bg-gray-100 text-gray-600'">
                {{ d.status === 'normal' ? '正常' : d.status === 'fault' ? '故障' : '离线' }}
              </span>
            </td>
            <td class="px-4 py-3 text-gray-400 text-xs">{{ d.last_data_at || '-' }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
const api = useApi();
const devices = ref<any[]>([]);
const filterType = ref("");
const filterStatus = ref("");
const errorMsg = ref("");

function typeLabel(t: string) {
  return { inverter: "逆变器", meter: "电表", combiner_box: "汇流箱", weather_station: "气象站", storage: "储能" }[t] || t;
}

async function fetchDevices() {
  try {
    errorMsg.value = "";
    const params: any = { page: 1, page_size: 100 };
    if (filterType.value) params.device_type = filterType.value;
    if (filterStatus.value) params.status = filterStatus.value;
    const res = await api.get("/devices", params);
    devices.value = res.items || [];
  } catch (e: any) {
    console.error("获取设备列表失败", e);
    errorMsg.value = "获取设备列表失败，请稍后重试";
  }
}

onMounted(fetchDevices);
</script>
