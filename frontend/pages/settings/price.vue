<template>
  <div>
    <h2 class="text-2xl font-bold text-gray-800 mb-6">电价配置</h2>

    <!-- 错误提示 -->
    <div v-if="errorMsg" class="bg-red-50 text-red-600 rounded-xl p-4 mb-6 text-sm">{{ errorMsg }}</div>

    <!-- 电站电价列表 -->
    <div class="bg-white rounded-xl shadow-sm overflow-hidden">
      <table class="w-full text-sm">
        <thead class="bg-gray-50 text-gray-500">
          <tr>
            <th class="px-4 py-3 text-left">电站名称</th>
            <th class="px-4 py-3 text-left">装机容量(kWp)</th>
            <th class="px-4 py-3 text-right">当前电价(元/kWh)</th>
            <th class="px-4 py-3 text-center">状态</th>
            <th class="px-4 py-3 text-center">操作</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr v-for="s in stations" :key="s.id" class="hover:bg-gray-50">
            <td class="px-4 py-3 font-medium text-gray-800">{{ s.name }}</td>
            <td class="px-4 py-3 text-gray-500">{{ s.capacity_kwp ?? '-' }}</td>
            <td class="px-4 py-3 text-right">
              <span v-if="editingId !== s.id" class="text-gray-800 font-medium">
                {{ s.electricity_price ?? '未设置' }}
              </span>
              <input
                v-else
                v-model.number="editPrice"
                type="number"
                step="0.01"
                min="0"
                class="w-24 px-2 py-1 border border-orange-300 rounded text-sm text-right outline-none focus:border-orange-500"
              />
            </td>
            <td class="px-4 py-3 text-center">
              <span class="px-2 py-1 text-xs rounded-full"
                :class="s.status === 'normal' ? 'bg-green-100 text-green-700' : s.status === 'fault' ? 'bg-red-100 text-red-700' : 'bg-gray-100 text-gray-600'">
                {{ s.status === 'normal' ? '正常' : s.status === 'fault' ? '故障' : '离线' }}
              </span>
            </td>
            <td class="px-4 py-3 text-center">
              <template v-if="editingId !== s.id">
                <button @click="startEdit(s)" class="text-orange-500 hover:text-orange-700 text-xs">编辑</button>
              </template>
              <template v-else>
                <button @click="savePrice(s.id)" class="text-green-500 hover:text-green-700 text-xs mr-2">保存</button>
                <button @click="cancelEdit" class="text-gray-400 hover:text-gray-600 text-xs">取消</button>
              </template>
            </td>
          </tr>
          <tr v-if="stations.length === 0">
            <td colspan="5" class="px-4 py-8 text-center text-gray-400">暂无电站</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
const api = useApi();
const stations = ref<any[]>([]);
const errorMsg = ref("");
const editingId = ref<number | null>(null);
const editPrice = ref<number>(0);

async function fetchStations() {
  try {
    errorMsg.value = "";
    const res = await api.get<any>("/stations", { page: 1, page_size: 100 });
    stations.value = res.items || res || [];
  } catch (e: any) {
    console.error("获取电站列表失败", e);
    errorMsg.value = "获取电站列表失败，请稍后重试";
  }
}

function startEdit(station: any) {
  editingId.value = station.id;
  editPrice.value = station.electricity_price || 0;
}

function cancelEdit() {
  editingId.value = null;
  editPrice.value = 0;
}

async function savePrice(stationId: number) {
  try {
    errorMsg.value = "";
    await api.put(`/stations/${stationId}`, { electricity_price: editPrice.value });
    editingId.value = null;
    await fetchStations();
  } catch (e: any) {
    console.error("保存电价失败", e);
    errorMsg.value = "保存电价失败，请稍后重试";
  }
}

onMounted(fetchStations);
</script>
