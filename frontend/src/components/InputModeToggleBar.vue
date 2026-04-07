<template>
  <div class="flex flex-wrap items-center justify-center gap-2">
    <button
      v-for="pill in modePills"
      :key="pill.mode"
      class="mode-pill"
      :class="activeMode === pill.mode ? 'mode-pill--active' : ''"
      @click="$emit('select-mode', activeMode === pill.mode ? 'normal' : pill.mode)">
      <span>{{ pill.icon }}</span>
      <span>{{ pill.label }}</span>
    </button>

    <div class="relative">
      <button class="mode-pill" @click="showMore = !showMore">
        <span>More</span>
      </button>
      <div v-if="showMore" class="mode-dropdown">
        <button v-for="item in moreItems" :key="item.label" class="mode-dropdown-item" @click="selectMore(item.mode, item.prompt)">
          <span>{{ item.icon }}</span>
          <span>{{ item.label }}</span>
        </button>
      </div>
    </div>

    <div v-if="activeMode === 'design'" class="relative">
      <button class="mode-pill mode-pill--secondary" @click="showDesignModels = !showDesignModels">
        <span>🍌</span>
        <span>{{ designModel }}</span>
        <span>▾</span>
      </button>
      <div v-if="showDesignModels" class="mode-dropdown">
        <button class="mode-dropdown-item" @click="pickDesignModel('Forge Image v1')">Forge Image v1</button>
        <button class="mode-dropdown-item" @click="pickDesignModel('Forge Image v2 Pro')">Forge Image v2 Pro</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import type { DesignModel, InputMode } from '../composables/useInputMode';

defineProps<{
  activeMode: InputMode;
  designModel: DesignModel;
}>();

const emit = defineEmits<{
  (e: 'select-mode', mode: InputMode): void;
  (e: 'apply-prompt', prompt: string): void;
  (e: 'update:designModel', model: DesignModel): void;
}>();

const showMore = ref(false);
const showDesignModels = ref(false);

const modePills: Array<{ mode: InputMode; label: string; icon: string }> = [
  { mode: 'wide_research', label: 'Wide Research', icon: '⊕' },
  { mode: 'slides', label: 'Create Slides', icon: '📋' },
  { mode: 'website', label: 'Build Website', icon: '🌐' },
  { mode: 'design', label: 'Design', icon: '✏️' },
];

const moreItems = [
  { icon: '📊', label: 'Spreadsheet', mode: 'spreadsheet' as InputMode, prompt: 'Create a spreadsheet for ' },
  { icon: '🔬', label: 'Wide Research', mode: 'wide_research' as InputMode, prompt: 'Conduct deep research on ' },
  { icon: '📹', label: 'Video', mode: 'video' as InputMode, prompt: 'Create a video plan for ' },
  { icon: '🎵', label: 'Audio', mode: 'audio' as InputMode, prompt: 'Create an audio brief for ' },
  { icon: '💬', label: 'Chat mode', mode: 'chat' as InputMode, prompt: '' },
  { icon: '📅', label: 'Schedule task', mode: 'schedule' as InputMode, prompt: 'Send me a daily market briefing every morning at 8am' },
  { icon: '📈', label: 'Visualization', mode: 'visualization' as InputMode, prompt: 'Create a KPI visualization for ' },
  { icon: '💻', label: 'Develop apps', mode: 'develop_apps' as InputMode, prompt: 'Build an app that ' },
  { icon: '📖', label: 'Playbook', mode: 'playbook' as InputMode, prompt: 'Create a playbook for ' },
];

const selectMore = (mode: InputMode, prompt: string) => {
  emit('select-mode', mode);
  emit('apply-prompt', prompt);
  showMore.value = false;
};

const pickDesignModel = (model: DesignModel) => {
  emit('update:designModel', model);
  showDesignModels.value = false;
};
</script>

<style scoped>
.mode-pill {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  border-radius: 9999px;
  border: 1px solid var(--border-main);
  background: var(--background-white-main);
  padding: 8px 14px;
  font-size: 13px;
  color: var(--text-secondary);
  transition: transform 0.18s ease, background-color 0.18s ease, border-color 0.18s ease, color 0.18s ease;
}

.mode-pill--active {
  background: #2563eb;
  border-color: #2563eb;
  color: white;
  transform: scale(1.03);
}

.mode-pill--secondary {
  background: #111827;
  border-color: #111827;
  color: white;
}

.mode-dropdown {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  width: 220px;
  border-radius: 18px;
  border: 1px solid var(--border-main);
  background: var(--background-white-main);
  box-shadow: 0px 18px 48px rgba(0, 0, 0, 0.12);
  padding: 8px;
  z-index: 40;
}

.mode-dropdown-item {
  display: flex;
  width: 100%;
  align-items: center;
  gap: 10px;
  border-radius: 12px;
  padding: 10px 12px;
  font-size: 13px;
  color: var(--text-primary);
  text-align: left;
}

.mode-dropdown-item:hover {
  background: var(--fill-tsp-white-light);
}
</style>
