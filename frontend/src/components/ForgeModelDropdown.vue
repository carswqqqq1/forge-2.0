<template>
  <div class="relative">
    <button class="flex items-center gap-2 h-9 px-3 rounded-full border border-[var(--border-btn-main)] bg-[var(--background-white-main)] shadow-[0px_1px_0px_rgba(0,0,0,0.03)]" @click="isOpen = !isOpen">
      <span class="text-sm font-medium text-[var(--text-primary)]">{{ currentTierMeta.shortLabel }}</span>
      <ChevronDown :size="14" class="text-[var(--icon-secondary)]" />
    </button>
    <div v-if="isOpen" class="absolute top-full left-0 mt-2 w-[320px] rounded-[18px] border border-[var(--border-main)] bg-[var(--background-white-main)] shadow-[0px_18px_48px_0px_rgba(0,0,0,0.12)] p-2 z-50">
      <button
        v-for="option in modelOptions"
        :key="option.key"
        class="w-full flex items-start gap-3 rounded-[14px] px-3 py-3 text-left hover:bg-[var(--fill-tsp-white-light)]"
        @click="select(option.key)">
        <Check :size="16" class="mt-0.5 shrink-0" :class="currentTier === option.key ? 'opacity-100 text-[var(--text-primary)]' : 'opacity-0'" />
        <div class="flex flex-col gap-1 min-w-0">
          <span class="text-[14px] font-medium text-[var(--text-primary)]">{{ option.title }}</span>
          <span class="text-[13px] text-[var(--text-secondary)]">{{ option.description }}</span>
          <span class="text-[12px] text-[var(--text-tertiary)]">{{ option.creditLabel }}</span>
        </div>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { ChevronDown, Check } from 'lucide-vue-next';
import { useModelTier, type ForgeModelTier } from '../composables/useModelTier';

const isOpen = ref(false);
const { currentTier, currentTierMeta, modelOptions, setModelTier } = useModelTier();

const select = (tier: ForgeModelTier) => {
  setModelTier(tier);
  isOpen.value = false;
};
</script>
