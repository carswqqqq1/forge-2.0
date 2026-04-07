<template>
  <div class="relative">
    <button class="credits-trigger" @click="isOpen = !isOpen">
      <Sparkles :size="14" />
      <span>{{ creditCount }}</span>
    </button>
    <div v-if="isOpen" class="credits-popover">
      <div class="flex items-center justify-between gap-3">
        <div>
          <div class="text-sm font-semibold text-[var(--text-primary)]">{{ planName }}</div>
          <div class="text-[12px] text-[var(--text-tertiary)]">Credit overview</div>
        </div>
        <button class="rounded-full bg-[var(--Button-primary-black)] px-3 py-1.5 text-[12px] font-medium text-[var(--text-onblack)]" @click="showInfoToast('Billing top-ups are coming soon')">
          Add credits
        </button>
      </div>
      <div class="mt-4 rounded-[18px] border border-[var(--border-main)] bg-[var(--background-gray-main)] p-3">
        <div class="text-[20px] font-semibold text-[var(--text-primary)]">✦ {{ creditCount }}</div>
        <div class="mt-3 grid grid-cols-1 gap-2 text-[12px] text-[var(--text-secondary)]">
          <div class="flex items-center justify-between"><span>Free</span><span>{{ currentUser?.free_credits ?? 0 }}</span></div>
          <div class="flex items-center justify-between"><span>Monthly</span><span>{{ currentUser?.monthly_credits ?? 0 }}/{{ currentUser?.monthly_credits_max ?? 0 }}</span></div>
          <div class="flex items-center justify-between"><span>Daily refresh</span><span>{{ currentUser?.daily_refresh_credits ?? 0 }}</span></div>
        </div>
      </div>
      <button class="mt-4 text-sm font-medium text-[var(--text-primary)] hover:opacity-80" @click="openUsage">
        View usage >
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import { Sparkles } from 'lucide-vue-next';
import { useAuth } from '../composables/useAuth';
import { useSettingsDialog } from '../composables/useSettingsDialog';
import { showInfoToast } from '../utils/toast';

const isOpen = ref(false);
const { currentUser } = useAuth();
const { openSettingsDialog } = useSettingsDialog();

const creditCount = computed(() => currentUser.value?.credits ?? 0);
const planName = computed(() => currentUser.value?.plan_name || 'Forge Pro');

const openUsage = () => {
  isOpen.value = false;
  openSettingsDialog('usage');
};
</script>

<style scoped>
.credits-trigger {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  height: 32px;
  padding: 0 12px;
  border-radius: 9999px;
  border: 1px solid var(--border-btn-main);
  background: var(--background-white-main);
  color: var(--text-secondary);
}

.credits-popover {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  width: 280px;
  border-radius: 22px;
  border: 1px solid var(--border-main);
  background: white;
  box-shadow: 0 24px 60px rgba(0, 0, 0, 0.14);
  padding: 16px;
  z-index: 60;
  animation: fadeIn 0.18s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(4px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
