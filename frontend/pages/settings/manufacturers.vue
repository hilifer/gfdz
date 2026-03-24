<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-2xl font-bold text-gray-800">厂家管理</h2>
      <button class="px-4 py-2 bg-orange-500 text-white rounded-lg text-sm hover:bg-orange-600">
        <i class="pi pi-plus mr-1"></i>添加厂家
      </button>
    </div>

    <!-- 错误提示 -->
    <div v-if="errorMsg" class="bg-red-50 text-red-600 rounded-xl p-4 mb-6 text-sm">{{ errorMsg }}</div>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
      <div v-for="m in manufacturers" :key="m.id" class="bg-white rounded-xl p-5 shadow-sm">
        <div class="flex items-center justify-between mb-3">
          <h3 class="font-semibold text-gray-800">{{ m.name }}</h3>
          <span class="px-2 py-1 text-xs rounded-full"
            :class="m.is_active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'">
            {{ m.is_active ? '已启用' : '已禁用' }}
          </span>
        </div>
        <dl class="space-y-2 text-sm">
          <div class="flex justify-between">
            <dt class="text-gray-500">编码</dt>
            <dd class="text-gray-800">{{ m.code }}</dd>
          </div>
          <div class="flex justify-between">
            <dt class="text-gray-500">API地址</dt>
            <dd class="text-gray-800 truncate max-w-[200px]">{{ m.api_base_url || '-' }}</dd>
          </div>
          <div class="flex justify-between">
            <dt class="text-gray-500">同步间隔</dt>
            <dd class="text-gray-800">{{ m.sync_interval }}秒</dd>
          </div>
          <div class="flex justify-between">
            <dt class="text-gray-500">最后同步</dt>
            <dd class="text-gray-400 text-xs">{{ formatSyncTime(m.last_sync_at) }}</dd>
          </div>
        </dl>
        <div class="mt-4 pt-3 border-t border-gray-100">
          <button
            @click="syncManufacturer(m.id)"
            :disabled="syncing === m.id"
            class="w-full px-3 py-2 bg-blue-50 text-blue-600 rounded-lg text-sm hover:bg-blue-100 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <i class="pi pi-refresh mr-1" :class="{ 'pi-spin': syncing === m.id }"></i>
            {{ syncing === m.id ? '同步中...' : '立即同步' }}
          </button>
        </div>
      </div>
    </div>

    <div v-if="manufacturers.length === 0 && !errorMsg" class="bg-white rounded-xl p-12 shadow-sm text-center text-gray-400">
      暂无厂家数据
    </div>
  </div>
</template>

<script setup lang="ts">
const api = useApi();
const manufacturers = ref<any[]>([]);
const errorMsg = ref("");
const syncing = ref<number | null>(null);

function formatSyncTime(t: string | null) {
  if (!t) return "未同步";
  try {
    return new Date(t).toLocaleString("zh-CN");
  } catch {
    return t;
  }
}

async function fetchManufacturers() {
  try {
    errorMsg.value = "";
    const res = await api.get<any>("/manufacturers");
    manufacturers.value = Array.isArray(res) ? res : res.items || [];
  } catch (e: any) {
    console.error("获取厂家列表失败", e);
    errorMsg.value = "获取厂家列表失败，请稍后重试";
  }
}

async function syncManufacturer(id: number) {
  try {
    syncing.value = id;
    errorMsg.value = "";
    await api.post(`/manufacturers/${id}/sync`);
    await fetchManufacturers();
  } catch (e: any) {
    console.error("同步失败", e);
    errorMsg.value = "同步失败，请稍后重试";
  } finally {
    syncing.value = null;
  }
}

onMounted(fetchManufacturers);
</script>
