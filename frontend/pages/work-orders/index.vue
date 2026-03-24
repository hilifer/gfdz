<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-2xl font-bold text-gray-800">工单管理</h2>
      <button @click="showCreateDialog = true" class="px-4 py-2 bg-orange-500 text-white rounded-lg text-sm hover:bg-orange-600">
        <i class="pi pi-plus mr-1"></i>创建工单
      </button>
    </div>

    <!-- 错误提示 -->
    <div v-if="errorMsg" class="bg-red-50 text-red-600 rounded-xl p-4 mb-6 text-sm">{{ errorMsg }}</div>

    <!-- 表格 -->
    <div class="bg-white rounded-xl shadow-sm overflow-hidden">
      <table class="w-full text-sm">
        <thead class="bg-gray-50 text-gray-500">
          <tr>
            <th class="px-4 py-3 text-left">工单编号</th>
            <th class="px-4 py-3 text-left">标题</th>
            <th class="px-4 py-3 text-left">电站</th>
            <th class="px-4 py-3 text-center">优先级</th>
            <th class="px-4 py-3 text-center">状态</th>
            <th class="px-4 py-3 text-left">创建人</th>
            <th class="px-4 py-3 text-left">创建时间</th>
            <th class="px-4 py-3 text-center">操作</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr v-for="o in orders" :key="o.id" class="hover:bg-gray-50">
            <td class="px-4 py-3 font-mono text-gray-600 text-xs">{{ o.order_no }}</td>
            <td class="px-4 py-3 font-medium text-gray-800">{{ o.title }}</td>
            <td class="px-4 py-3 text-gray-500">{{ o.station_name || o.station || '-' }}</td>
            <td class="px-4 py-3 text-center">
              <span class="px-2 py-1 text-xs rounded-full" :class="priorityClass(o.priority)">
                {{ priorityLabel(o.priority) }}
              </span>
            </td>
            <td class="px-4 py-3 text-center">
              <span class="px-2 py-1 text-xs rounded-full" :class="statusClass(o.status)">
                {{ statusLabel(o.status) }}
              </span>
            </td>
            <td class="px-4 py-3 text-gray-500">{{ o.creator_name || o.creator || '-' }}</td>
            <td class="px-4 py-3 text-gray-400 text-xs">{{ o.created_at }}</td>
            <td class="px-4 py-3 text-center">
              <button
                v-if="o.status !== 'completed' && o.status !== 'closed'"
                @click="completeOrder(o.id)"
                class="text-green-500 hover:text-green-700 text-xs"
              >
                完成
              </button>
              <span v-else class="text-gray-400 text-xs">-</span>
            </td>
          </tr>
          <tr v-if="orders.length === 0">
            <td colspan="8" class="px-4 py-8 text-center text-gray-400">暂无工单</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 创建工单弹窗 -->
    <div v-if="showCreateDialog" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-xl p-6 w-full max-w-lg shadow-xl">
        <h3 class="text-lg font-semibold text-gray-800 mb-4">创建工单</h3>
        <div class="space-y-4">
          <div>
            <label class="block text-sm text-gray-600 mb-1">标题</label>
            <input v-model="form.title" type="text" class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm outline-none focus:border-orange-400" placeholder="请输入工单标题" />
          </div>
          <div>
            <label class="block text-sm text-gray-600 mb-1">电站</label>
            <select v-model="form.station_id" class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm outline-none focus:border-orange-400">
              <option value="">请选择电站</option>
              <option v-for="s in stations" :key="s.id" :value="s.id">{{ s.name }}</option>
            </select>
          </div>
          <div>
            <label class="block text-sm text-gray-600 mb-1">优先级</label>
            <select v-model="form.priority" class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm outline-none focus:border-orange-400">
              <option value="low">低</option>
              <option value="medium">中</option>
              <option value="high">高</option>
              <option value="urgent">紧急</option>
            </select>
          </div>
          <div>
            <label class="block text-sm text-gray-600 mb-1">描述</label>
            <textarea v-model="form.description" rows="3" class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm outline-none focus:border-orange-400" placeholder="请输入工单描述"></textarea>
          </div>
        </div>
        <div class="flex justify-end space-x-3 mt-6">
          <button @click="showCreateDialog = false" class="px-4 py-2 text-gray-600 border border-gray-300 rounded-lg text-sm hover:bg-gray-50">取消</button>
          <button @click="createOrder" class="px-4 py-2 bg-orange-500 text-white rounded-lg text-sm hover:bg-orange-600">创建</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const api = useApi();
const orders = ref<any[]>([]);
const stations = ref<any[]>([]);
const errorMsg = ref("");
const showCreateDialog = ref(false);
const form = ref({
  title: "",
  station_id: "",
  priority: "medium",
  description: "",
});

function priorityLabel(p: string) {
  return { low: "低", medium: "中", high: "高", urgent: "紧急" }[p] || p;
}

function priorityClass(p: string) {
  return {
    low: "bg-gray-100 text-gray-600",
    medium: "bg-blue-100 text-blue-700",
    high: "bg-orange-100 text-orange-700",
    urgent: "bg-red-100 text-red-700",
  }[p] || "bg-gray-100 text-gray-600";
}

function statusLabel(s: string) {
  return { pending: "待处理", in_progress: "处理中", completed: "已完成", closed: "已关闭" }[s] || s;
}

function statusClass(s: string) {
  return {
    pending: "bg-yellow-100 text-yellow-700",
    in_progress: "bg-blue-100 text-blue-700",
    completed: "bg-green-100 text-green-700",
    closed: "bg-gray-100 text-gray-600",
  }[s] || "bg-gray-100 text-gray-600";
}

async function fetchOrders() {
  try {
    errorMsg.value = "";
    const res = await api.get<any>("/work-orders", { page: 1, page_size: 100 });
    orders.value = res.items || res || [];
  } catch (e: any) {
    console.error("获取工单列表失败", e);
    errorMsg.value = "获取工单列表失败，请稍后重试";
  }
}

async function fetchStations() {
  try {
    const res = await api.get<any>("/stations", { page: 1, page_size: 100 });
    stations.value = res.items || res || [];
  } catch (e: any) {
    console.error("获取电站列表失败", e);
  }
}

async function createOrder() {
  try {
    errorMsg.value = "";
    await api.post("/work-orders", {
      title: form.value.title,
      station_id: form.value.station_id ? Number(form.value.station_id) : undefined,
      priority: form.value.priority,
      description: form.value.description,
    });
    showCreateDialog.value = false;
    form.value = { title: "", station_id: "", priority: "medium", description: "" };
    fetchOrders();
  } catch (e: any) {
    console.error("创建工单失败", e);
    errorMsg.value = "创建工单失败，请稍后重试";
  }
}

async function completeOrder(id: number) {
  try {
    errorMsg.value = "";
    await api.post(`/work-orders/${id}/complete`);
    fetchOrders();
  } catch (e: any) {
    console.error("完成工单失败", e);
    errorMsg.value = "完成工单失败，请稍后重试";
  }
}

onMounted(() => {
  fetchOrders();
  fetchStations();
});
</script>
