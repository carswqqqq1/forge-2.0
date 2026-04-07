<template>
  <div class="[&:not(:empty)]:pb-2 bg-[var(--background-gray-main)] rounded-[22px_22px_0px_0px]">
    <div v-if="isExpanded" class="border border-black/8 bg-[var(--background-menu-white)] rounded-[16px] shadow-[0px_0px_1px_0px_rgba(0,0,0,0.05),_0px_8px_32px_0px_rgba(0,0,0,0.04)] flex flex-col py-4">
      <div class="px-4 flex items-center justify-between">
        <div class="text-sm font-semibold text-[var(--text-primary)]">Task Progress</div>
        <button class="flex h-7 w-7 items-center justify-center rounded-md hover:bg-[var(--fill-tsp-gray-main)]" @click="togglePanel">
          <ChevronDown :size="16" class="text-[var(--icon-tertiary)]" />
        </button>
      </div>

      <div class="mt-3 px-4 flex flex-col gap-3 max-h-[420px] overflow-y-auto">
        <div v-for="step in props.plan.steps" :key="step.id" class="rounded-[16px] border border-[var(--border-main)] bg-[var(--background-gray-main)] px-4 py-3">
          <div class="flex items-start justify-between gap-3">
            <div class="flex items-start gap-3 min-w-0">
              <div class="mt-0.5">
                <div v-if="step.status === 'running'" class="w-5 h-5 rounded-full border-2 border-[#3b82f6] border-t-transparent animate-spin"></div>
                <div v-else-if="step.status === 'completed'" class="w-5 h-5 rounded-full bg-[#16a34a] text-white flex items-center justify-center">
                  <Check :size="12" />
                </div>
                <div v-else class="w-5 h-5 rounded-full border border-[var(--border-main)] bg-white"></div>
              </div>
              <div class="min-w-0">
                <div class="text-sm font-semibold text-[var(--text-primary)]">{{ step.description }}</div>
                <div class="mt-2 flex flex-wrap gap-2">
                  <span v-for="chip in stepChips(step.description)" :key="chip" class="step-chip">{{ chip }}</span>
                  <button class="step-chip" @click="knowledgeExpanded = !knowledgeExpanded">
                    ⚡ Knowledge recalled({{ knowledgeCount }}) ▾
                  </button>
                </div>
                <div v-if="knowledgeExpanded" class="mt-2 rounded-[12px] bg-white px-3 py-2 text-[12px] leading-6 text-[var(--text-secondary)]">
                  Forge is carrying forward recent context, task history, and user preferences from this workspace.
                </div>
              </div>
            </div>
            <button class="text-[var(--icon-secondary)]" @click="togglePanel">
              <ChevronUp :size="16" />
            </button>
          </div>
        </div>
      </div>
    </div>

    <div v-else @click="togglePanel" class="flex flex-row items-start justify-between pe-3 relative clickable border border-black/8 rounded-[16px] shadow-[0px_0px_1px_0px_rgba(0,0,0,0.05),_0px_8px_32px_0px_rgba(0,0,0,0.04)]" :class="isCompleted ? 'bg-[#f0fdf4] border-[#bbf7d0]' : 'bg-[var(--background-menu-white)]'">
      <div class="flex-1 min-w-0 relative overflow-hidden">
        <div class="flex items-start gap-2.5 w-full px-4 py-2 truncate">
          <div v-if="isCompleted" class="w-4 h-4 rounded-full bg-[#16a34a] text-white flex items-center justify-center shrink-0">
            <Check :size="10" />
          </div>
          <div v-else class="w-4 h-4 rounded-full border border-[var(--border-main)] bg-white shrink-0"></div>
          <div class="flex flex-col w-full gap-[2px] truncate">
            <div class="text-sm truncate" :title="currentStep" :style="{ color: isCompleted ? '#15803d' : 'var(--text-tertiary)' }">
              {{ currentStep }}
            </div>
          </div>
        </div>
      </div>
      <button class="flex h-full cursor-pointer justify-center gap-2 flex-shrink-0 items-start py-2.5">
        <span class="text-xs hidden sm:flex" :style="{ color: isCompleted ? '#15803d' : 'var(--text-tertiary)' }">{{ planProgress }}</span>
        <ChevronUp class="text-[var(--icon-tertiary)]" :size="16" />
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import { ChevronUp, ChevronDown, Check } from 'lucide-vue-next';
import type { PlanEventData } from '../types/event';

const props = defineProps<{
  plan: PlanEventData;
}>();

const isExpanded = ref(false);
const knowledgeExpanded = ref(false);

const togglePanel = () => {
  isExpanded.value = !isExpanded.value;
};

const stepChips = (description: string) => {
  const words = description.split(' ').filter(Boolean).slice(0, 4).join(' ');
  return [`📄 ${words}`, '📝 Review context'];
};

const knowledgeCount = computed(() => Math.max(1, Math.min(3, props.plan.steps.length)));

const planProgress = computed(() => {
  const completedSteps = props.plan?.steps.filter(step => step.status === 'completed').length ?? 0;
  return `${completedSteps}/${props.plan?.steps.length ?? 1}`;
});

const isCompleted = computed(() => props.plan?.steps.every(step => step.status === 'completed') ?? false);

const currentStep = computed(() => {
  for (const step of props.plan?.steps ?? []) {
    if (step.status === 'running' || step.status === 'pending') return step.description;
  }
  return 'Task completed';
});
</script>

<style scoped>
.step-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  height: 28px;
  padding: 0 10px;
  border-radius: 9999px;
  border: 1px solid rgba(17, 24, 39, 0.08);
  background: #111827;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.92);
}
</style>
