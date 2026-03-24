<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-2xl font-bold text-gray-800">用户管理</h2>
      <button class="px-4 py-2 bg-orange-500 text-white rounded-lg text-sm hover:bg-orange-600">
        <i class="pi pi-plus mr-1"></i>添加用户
      </button>
    </div>

    <!-- 错误提示 -->
    <div v-if="errorMsg" class="bg-red-50 text-red-600 rounded-xl p-4 mb-6 text-sm">{{ errorMsg }}</div>

    <div class="bg-white rounded-xl shadow-sm overflow-hidden">
      <table class="w-full text-sm">
        <thead class="bg-gray-50 text-gray-500">
          <tr>
            <th class="px-4 py-3 text-left">用户名</th>
            <th class="px-4 py-3 text-left">显示名称</th>
            <th class="px-4 py-3 text-left">角色</th>
            <th class="px-4 py-3 text-left">手机</th>
            <th class="px-4 py-3 text-center">状态</th>
            <th class="px-4 py-3 text-left">最后登录</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr v-for="u in users" :key="u.id" class="hover:bg-gray-50">
            <td class="px-4 py-3 font-medium text-gray-800">{{ u.username }}</td>
            <td class="px-4 py-3 text-gray-500">{{ u.display_name }}</td>
            <td class="px-4 py-3 text-gray-500">{{ roleLabel(u.role) }}</td>
            <td class="px-4 py-3 text-gray-500">{{ u.phone || '-' }}</td>
            <td class="px-4 py-3 text-center">
              <span class="px-2 py-1 text-xs rounded-full" :class="u.is_active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'">
                {{ u.is_active ? '启用' : '禁用' }}
              </span>
            </td>
            <td class="px-4 py-3 text-gray-400 text-xs">{{ u.last_login_at || '-' }}</td>
          </tr>
          <tr v-if="users.length === 0">
            <td colspan="6" class="px-4 py-8 text-center text-gray-400">暂无用户</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
const api = useApi();
const users = ref<any[]>([]);
const errorMsg = ref("");

function roleLabel(r: string) {
  return { admin: "管理员", operator: "运维员", viewer: "查看者" }[r] || r;
}

async function fetchUsers() {
  try {
    errorMsg.value = "";
    const res = await api.get<any>("/system/users");
    users.value = Array.isArray(res) ? res : res.items || [];
  } catch (e: any) {
    console.error("获取用户列表失败", e);
    errorMsg.value = "获取用户列表失败，请稍后重试";
  }
}

onMounted(fetchUsers);
</script>
