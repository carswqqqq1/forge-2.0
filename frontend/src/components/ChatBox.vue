<template>
  <div class="pb-3 relative bg-[var(--background-gray-main)]">
    <div class="flex flex-col gap-2">
      <div
        class="flex flex-col gap-2 rounded-[22px] transition-all relative bg-[var(--fill-input-chat)] py-3 shadow-[0px_12px_32px_0px_rgba(0,0,0,0.02)] border border-black/8 dark:border-[var(--border-main)]">
        <ChatBoxFiles ref="chatBoxFileListRef" :attachments="attachments" />
        <div class="overflow-y-auto pl-4 pr-3">
          <textarea
            class="flex rounded-md border-input focus-visible:outline-none disabled:cursor-not-allowed disabled:opacity-50 overflow-hidden flex-1 bg-transparent p-0 pt-[1px] border-0 w-full placeholder:text-[var(--text-disable)] text-[15px] shadow-none resize-none min-h-[74px]"
            :rows="rows"
            :value="modelValue"
            @input="$emit('update:modelValue', ($event.target as HTMLTextAreaElement).value)"
            @compositionstart="isComposing = true"
            @compositionend="isComposing = false"
            @keydown.enter.exact="handleEnterKeydown"
            :placeholder="props.disabled ? 'Out of credits' : (props.placeholder || 'Assign a task to Forge...')"
            :disabled="props.disabled"></textarea>
        </div>

        <footer class="flex flex-row justify-between items-center w-full px-3">
          <div class="flex gap-1 pr-2 items-center">
            <button class="toolbar-button" :disabled="props.disabled" @click="uploadFile"><Plus :size="16" /></button>
            <button class="toolbar-button" :disabled="props.disabled" @click="openConnectModal('GitHub')"><Github :size="16" /></button>
            <button class="toolbar-button" :disabled="props.disabled" @click="showInfoToast('Browser tools are available')"><Globe :size="16" /></button>
            <button class="toolbar-button" :disabled="props.disabled" @click="showInfoToast('Computer controls are available in active runs')"><Monitor :size="16" /></button>
          </div>

          <div class="flex gap-1 items-center">
            <button class="toolbar-button" :disabled="props.disabled" @click="showInfoToast('Reactions coming soon')"><Smile :size="16" /></button>
            <button class="toolbar-button" :disabled="props.disabled" @click="showInfoToast('Voice input is not supported yet')"><Mic :size="16" /></button>
            <button
              v-if="!isRunning || sendEnabled || hideStopButton"
              :disabled="props.disabled || !sendEnabled"
              class="whitespace-nowrap text-sm font-medium disabled:pointer-events-none disabled:opacity-50 p-0 w-8 h-8 rounded-full flex items-center justify-center transition-colors"
              :class="!sendEnabled ? 'cursor-not-allowed bg-[var(--fill-tsp-white-dark)]' : 'cursor-pointer bg-[var(--Button-primary-black)]'"
              @click="handleSubmit">
              <SendIcon :disabled="!sendEnabled" />
            </button>
            <button
              v-else-if="!hideStopButton"
              @click="handleStop"
              class="inline-flex items-center justify-center bg-[var(--Button-primary-black)] text-[var(--text-onblack)] rounded-full p-0 w-8 h-8">
              <div class="w-[10px] h-[10px] bg-[var(--icon-onblack)] rounded-[2px]"></div>
            </button>
          </div>
        </footer>
      </div>

      <div class="flex flex-wrap gap-2 px-1">
        <button v-for="tool in tools" :key="tool.name" class="tool-pill" @click="toggleTool(tool.name)">
          <component :is="tool.icon" :size="14" />
          <span>{{ tool.name }}</span>
          <span class="text-[10px] opacity-70">{{ connectedTools[tool.name] ? 'Connected' : 'Available' }}</span>
        </button>
      </div>

      <div v-if="!connectBarDismissed" class="flex items-center justify-between gap-3 rounded-full border border-[var(--border-main)] bg-[var(--background-white-main)] px-3 py-2">
        <div class="flex items-center gap-2 min-w-0">
          <span class="text-[12px] text-[var(--text-secondary)] whitespace-nowrap">Connect your tools to Forge</span>
          <div class="flex items-center gap-1 overflow-hidden">
            <button v-for="integration in integrations" :key="integration" class="connect-logo-btn" @click="openConnectModal(integration)">
              <IntegrationLogo :name="integration" />
            </button>
          </div>
        </div>
        <button class="flex h-6 w-6 items-center justify-center rounded-full hover:bg-[var(--fill-tsp-white-light)]" @click="dismissConnectBar">
          <X :size="14" />
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue';
import SendIcon from './icons/SendIcon.vue';
import ChatBoxFiles from './ChatBoxFiles.vue';
import { Plus, Github, Globe, Monitor, Smile, Mic, Terminal, FileText, Search, X } from 'lucide-vue-next';
import type { FileInfo } from '../api/file';
import { showInfoToast } from '../utils/toast';
import { useConnectModal, type IntegrationName } from '../composables/useConnectModal';
import IntegrationLogo from './IntegrationLogo.vue';

const hasTextInput = ref(false);
const isComposing = ref(false);
const chatBoxFileListRef = ref();
const connectBarDismissed = ref(localStorage.getItem('forge-connect-bar-dismissed') === 'true');
const { openConnectModal } = useConnectModal();
const connectedTools = ref<Record<string, boolean>>({
    Browser: false,
    Terminal: false,
    File: false,
    Search: false,
});

const tools = [
    { name: 'Browser', icon: Globe },
    { name: 'Terminal', icon: Terminal },
    { name: 'File', icon: FileText },
    { name: 'Search', icon: Search },
];
const integrations: IntegrationName[] = ['Notion', 'Gmail', 'Google Calendar', 'GitHub', 'Slack', 'Database', 'Browser'];

const props = defineProps<{
    modelValue: string;
    rows: number;
    isRunning: boolean;
    attachments: FileInfo[];
    disabled?: boolean;
    hideStopButton?: boolean;
    allowSendFilesOnly?: boolean;
    placeholder?: string;
}>();

const sendEnabled = computed(() => {
    const hasFiles = (props.attachments?.length ?? 0) > 0;
    const allUploaded = chatBoxFileListRef.value?.isAllUploaded ?? true;
    if (props.allowSendFilesOnly) {
        return hasTextInput.value || (hasFiles && allUploaded);
    }
    return hasTextInput.value && (!hasFiles || allUploaded);
});

const emit = defineEmits<{
    (e: 'update:modelValue', value: string): void;
    (e: 'submit'): void;
    (e: 'stop'): void;
}>();

const handleEnterKeydown = (event: KeyboardEvent) => {
    if (isComposing.value) return;
    if (sendEnabled.value) {
        event.preventDefault();
        handleSubmit();
    }
};

const handleSubmit = () => {
    if (!sendEnabled.value || props.disabled) return;
    emit('submit');
};

const handleStop = () => {
    if (props.disabled) return;
    emit('stop');
};

const uploadFile = () => {
    if (props.disabled) return;
    chatBoxFileListRef.value?.uploadFile();
};

const toggleTool = (toolName: string) => {
    connectedTools.value[toolName] = !connectedTools.value[toolName];
    showInfoToast(`${toolName} ${connectedTools.value[toolName] ? 'connected' : 'disconnected'}`);
};

const dismissConnectBar = () => {
    connectBarDismissed.value = true;
    localStorage.setItem('forge-connect-bar-dismissed', 'true');
};

watch(() => props.modelValue, (value) => {
    hasTextInput.value = value.trim() !== '';
}, { immediate: true });
</script>

<style scoped>
.toolbar-button {
    width: 32px;
    height: 32px;
    border-radius: 9999px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    color: var(--text-secondary);
    transition: background-color 0.15s ease;
}

.toolbar-button:hover {
    background: var(--fill-tsp-gray-main);
}

.tool-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    height: 28px;
    padding: 0 10px;
    border-radius: 9999px;
    border: 1px solid var(--border-main);
    background: var(--background-white-main);
    font-size: 12px;
    color: var(--text-secondary);
}

.connect-logo-btn {
    width: 28px;
    height: 28px;
    border-radius: 9999px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    background: var(--fill-tsp-white-light);
    transition: transform 0.15s ease, background-color 0.15s ease;
}

.connect-logo-btn:hover {
    background: var(--background-gray-main);
    transform: translateY(-1px);
}
</style>
