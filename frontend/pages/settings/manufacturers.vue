<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-2xl font-bold text-gray-800">厂家管理</h2>
      <button class="px-4 py-2 bg-orange-500 text-white rounded-lg text-sm hover:bg-orange-600">
        <i class="pi pi-plus mr-1"></i>添加厂家
      </button>
    </div>

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
            <dd class="text-gray-400 text-xs">{{ m.last_sync_at || '未同步' }}</dd>
          </div>
        </dl>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const api = useApi();
const manufacturers = ref<any[]>([]);

onMounted(async () => {
  manufacturers.value = await api.get("/manufacturers");
});
</script>
