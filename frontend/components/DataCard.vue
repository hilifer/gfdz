<template>
  <div class="bg-white rounded-xl p-5 shadow-sm hover:shadow-md transition-shadow">
    <div class="flex items-center justify-between">
      <div>
        <p class="text-sm text-gray-500">{{ title }}</p>
        <p class="text-2xl font-bold mt-1" :class="textColor">
          {{ value }}
          <span class="text-sm font-normal text-gray-400">{{ unit }}</span>
        </p>
      </div>
      <div
        class="w-12 h-12 rounded-lg flex items-center justify-center"
        :class="bgColor"
      >
        <i :class="icon" class="text-xl" :class="iconColor"></i>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  title: string;
  value: string | number;
  unit?: string;
  icon: string;
  color: string;
}>();

const colorMap: Record<string, { bg: string; icon: string; text: string }> = {
  blue:   { bg: "bg-blue-50",   icon: "text-blue-500",   text: "text-blue-600" },
  orange: { bg: "bg-orange-50", icon: "text-orange-500", text: "text-orange-600" },
  green:  { bg: "bg-green-50",  icon: "text-green-500",  text: "text-green-600" },
  purple: { bg: "bg-purple-50", icon: "text-purple-500", text: "text-purple-600" },
  red:    { bg: "bg-red-50",    icon: "text-red-500",    text: "text-red-600" },
  cyan:   { bg: "bg-cyan-50",   icon: "text-cyan-500",   text: "text-cyan-600" },
};

const c = computed(() => colorMap[props.color] || colorMap.blue);
const bgColor = computed(() => c.value.bg);
const iconColor = computed(() => c.value.icon);
const textColor = computed(() => c.value.text);
</script>
