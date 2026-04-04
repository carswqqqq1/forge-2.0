<template>
  <SimpleBar>
    <div class="flex flex-col h-full flex-1 min-w-0 mx-auto w-full px-5 relative max-w-full">
      <div class="w-full pt-4 pb-4 px-5 bg-[var(--background-gray-main)] sticky top-0 z-10 mx-[-1.25]">
        <div class="flex justify-between items-center w-full absolute left-0 right-0">
          <div class="h-8 relative z-20 overflow-hidden flex gap-2 items-center flex-shrink-0">
            <div class="relative flex items-center">
              <div
                v-if="!isLeftPanelShow"
                class="flex h-7 w-7 items-center justify-center cursor-pointer rounded-md hover:bg-[var(--fill-tsp-gray-main)]"
                @click="toggleLeftPanel">
                <PanelLeft class="size-5 text-[var(--icon-secondary)]" />
              </div>
            </div>
            <div class="flex">
              <Bot :size="30" />
              <ManusLogoTextIcon />
            </div>
          </div>
          <div class="flex items-center gap-2">
            <a
              v-if="showGithubButton"
              :href="githubRepositoryUrl"
              target="_blank"
              rel="noopener noreferrer"
              class="items-center justify-center whitespace-nowrap font-medium transition-colors hover:opacity-90 active:opacity-80 px-[12px] gap-[6px] text-sm min-w-16 outline outline-1 -outline-offset-1 hover:bg-[var(--fill-tsp-white-light)] text-[var(--text-primary)] outline-[var(--border-btn-main)] bg-transparent clickable hidden sm:flex rounded-[100px] relative h-[32px] group"
              title="Visit GitHub Repository">
              <Github class="size-[18px]" />
              GitHub
            </a>
            <div
              class="relative flex items-center"
              aria-expanded="false"
              aria-haspopup="dialog"
              @mouseenter="handleUserMenuEnter"
              @mouseleave="handleUserMenuLeave">
              <div class="relative flex items-center justify-center font-bold cursor-pointer flex-shrink-0">
                <div
                  class="relative flex items-center justify-center font-bold flex-shrink-0 rounded-full overflow-hidden"
                  style="width: 32px; height: 32px; font-size: 16px; color: rgba(255, 255, 255, 0.9); background-color: rgb(59, 130, 246);">
                  {{ avatarLetter }}
                </div>
              </div>
              <div
                v-if="showUserMenu"
                class="absolute top-full right-0 mt-1 mr-[-15px] z-50"
                @mouseenter="handleUserMenuEnter"
                @mouseleave="handleUserMenuLeave">
                <UserMenu />
              </div>
            </div>
          </div>
        </div>
        <div class="h-8"></div>
      </div>

      <div class="w-full max-w-[920px] mx-auto mt-10 md:mt-16 pb-10">
        <div class="w-full flex flex-col gap-2 pb-6">
          <span
            class="text-[var(--text-primary)] text-start font-serif text-[32px] leading-[40px]"
            style="font-family: ui-serif, Georgia, Cambria, 'Times New Roman', Times, serif;">
            {{ $t('Hello') }}, {{ currentUser?.fullname }}
          </span>
          <span class="text-[var(--text-tertiary)] text-base leading-7">
            {{ $t('What can I do for you?') }}
          </span>
        </div>

        <section class="rounded-[28px] border border-[var(--border-main)] bg-[var(--background-menu-white)] shadow-[0px_16px_48px_0px_var(--shadow-S)] overflow-hidden mb-6">
          <div class="px-5 pt-5 pb-4 border-b border-[var(--border-light)]">
            <div class="flex flex-col gap-2 md:flex-row md:items-end md:justify-between">
              <div class="flex flex-col gap-1">
                <div class="text-[var(--text-primary)] text-lg font-semibold">{{ t('Forge Studio') }}</div>
                <div class="text-[13px] text-[var(--text-tertiary)]">
                  {{ t('Launch a task with the right workspace, preset, and model stack already loaded.') }}
                </div>
              </div>
              <div class="inline-flex items-center gap-2 rounded-full bg-[var(--fill-tsp-white-main)] px-3 py-1.5 text-[12px] text-[var(--text-secondary)]">
                <Sparkles :size="14" />
                <span>{{ memorySummary }}</span>
              </div>
            </div>
          </div>

          <div class="px-5 py-5 flex flex-col gap-5">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <label class="flex flex-col gap-2">
                <span class="text-[13px] font-medium text-[var(--text-secondary)]">{{ t('Workspace') }}</span>
                <select v-model="selectedWorkspaceId" class="studio-input">
                  <option value="">{{ t('Personal Inbox') }}</option>
                  <option v-for="workspace in workspaces" :key="workspace.id" :value="workspace.id">
                    {{ workspace.name }}
                  </option>
                </select>
              </label>

              <label class="flex flex-col gap-2">
                <span class="text-[13px] font-medium text-[var(--text-secondary)]">{{ t('Agent Preset') }}</span>
                <select v-model="selectedPresetId" class="studio-input">
                  <option value="">{{ t('No preset') }}</option>
                  <option v-for="preset in presets" :key="preset.id" :value="preset.id">
                    {{ preset.name }}
                  </option>
                </select>
              </label>

              <label class="flex flex-col gap-2">
                <span class="text-[13px] font-medium text-[var(--text-secondary)]">{{ t('Model Provider') }}</span>
                <input v-model="selectedModelProvider" class="studio-input" type="text" />
              </label>

              <label class="flex flex-col gap-2">
                <span class="text-[13px] font-medium text-[var(--text-secondary)]">{{ t('Model Name') }}</span>
                <input v-model="selectedModelName" class="studio-input" type="text" />
              </label>

              <label class="flex flex-col gap-2">
                <span class="text-[13px] font-medium text-[var(--text-secondary)]">{{ t('Temperature') }}</span>
                <input v-model.number="selectedTemperature" class="studio-input" type="number" min="0" max="1" step="0.1" />
              </label>

              <label class="flex flex-col gap-2">
                <span class="text-[13px] font-medium text-[var(--text-secondary)]">{{ t('Max Tokens') }}</span>
                <input v-model.number="selectedMaxTokens" class="studio-input" type="number" min="256" step="256" />
              </label>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-[1.3fr_0.7fr] gap-4">
              <div class="rounded-[22px] bg-[var(--fill-tsp-white-main)] border border-[var(--border-light)] px-4 py-4 flex flex-col gap-3">
                <div class="flex items-center justify-between gap-3">
                  <div class="flex flex-col gap-1">
                    <div class="text-sm font-medium text-[var(--text-primary)]">{{ activePresetTitle }}</div>
                    <div class="text-[13px] text-[var(--text-tertiary)]">
                      {{ activePresetDescription }}
                    </div>
                  </div>
                  <div class="inline-flex items-center gap-1 rounded-full bg-[var(--background-menu-white)] px-3 py-1 text-[12px] text-[var(--text-secondary)]">
                    <Bot :size="13" />
                    <span>{{ activeWorkspaceLabel }}</span>
                  </div>
                </div>
                <div class="text-[13px] leading-6 text-[var(--text-secondary)]">
                  {{ activeInstructionsPreview }}
                </div>
              </div>

              <div class="rounded-[22px] bg-[var(--fill-tsp-white-main)] border border-[var(--border-light)] px-4 py-4 flex flex-col gap-3">
                <div class="text-sm font-medium text-[var(--text-primary)]">{{ t('Memory Pack') }}</div>
                <div v-if="memories.length > 0" class="flex flex-wrap gap-2">
                  <span
                    v-for="memory in memories.slice(0, 4)"
                    :key="memory.id"
                    class="inline-flex items-center rounded-full bg-[var(--background-menu-white)] px-3 py-1.5 text-[12px] text-[var(--text-secondary)] max-w-full">
                    <span class="truncate">{{ memory.content }}</span>
                  </span>
                </div>
                <div v-else class="text-[13px] leading-6 text-[var(--text-tertiary)]">
                  {{ t('No saved memory yet. Add context from Settings > Studio to make Forge feel personalized.') }}
                </div>
              </div>
            </div>
          </div>
        </section>

        <div class="flex flex-col gap-1 w-full">
          <div class="flex flex-col bg-[var(--background-gray-main)] w-full">
            <ChatBox :rows="2" v-model="message" @submit="handleSubmit" :isRunning="false" :attachments="attachments" />
          </div>
        </div>
      </div>
    </div>
  </SimpleBar>
</template>

<script setup lang="ts">
import SimpleBar from '../components/SimpleBar.vue';
import { ref, onMounted, computed, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';
import ChatBox from '../components/ChatBox.vue';
import { createSession } from '../api/agent';
import { type AgentPreset, type ForgeProfile, type Workspace } from '../api/auth';
import { showErrorToast } from '../utils/toast';
import { Bot, PanelLeft, Github, Sparkles } from 'lucide-vue-next';
import ManusLogoTextIcon from '../components/icons/ManusLogoTextIcon.vue';
import type { FileInfo } from '../api/file';
import { useLeftPanel } from '../composables/useLeftPanel';
import { useFilePanel } from '../composables/useFilePanel';
import { useAuth } from '../composables/useAuth';
import { getCachedClientConfig } from '../api/config';
import UserMenu from '../components/UserMenu.vue';

const DEFAULT_FORGE_PROFILE: ForgeProfile = {
  model_preferences: {
    model_provider: 'openai',
    model_name: 'gpt-4o',
    temperature: 0.7,
    max_tokens: 2000,
  },
  memories: [],
  workspaces: [],
  agent_presets: [],
};

const { t } = useI18n();
const router = useRouter();
const message = ref('');
const isSubmitting = ref(false);
const attachments = ref<FileInfo[]>([]);
const { toggleLeftPanel, isLeftPanelShow } = useLeftPanel();
const { hideFilePanel } = useFilePanel();
const { currentUser } = useAuth();
const showGithubButton = ref(false);
const githubRepositoryUrl = ref('https://github.com/simpleyyt/ai-manus');

const selectedWorkspaceId = ref('');
const selectedPresetId = ref('');
const selectedModelProvider = ref(DEFAULT_FORGE_PROFILE.model_preferences.model_provider);
const selectedModelName = ref(DEFAULT_FORGE_PROFILE.model_preferences.model_name);
const selectedTemperature = ref(DEFAULT_FORGE_PROFILE.model_preferences.temperature);
const selectedMaxTokens = ref(DEFAULT_FORGE_PROFILE.model_preferences.max_tokens);

const forgeProfile = computed<ForgeProfile>(() => currentUser.value?.forge_profile || DEFAULT_FORGE_PROFILE);
const workspaces = computed(() => forgeProfile.value.workspaces);
const presets = computed(() => forgeProfile.value.agent_presets);
const memories = computed(() => forgeProfile.value.memories);

const selectedPreset = computed<AgentPreset | null>(() => {
  return presets.value.find((preset) => preset.id === selectedPresetId.value) || null;
});

const activeWorkspace = computed<Workspace | null>(() => {
  return workspaces.value.find((workspace) => workspace.id === selectedWorkspaceId.value) || null;
});

const avatarLetter = computed(() => currentUser.value?.fullname?.charAt(0)?.toUpperCase() || 'M');

const memorySummary = computed(() => {
  if (memories.value.length === 0) {
    return t('No memories loaded');
  }
  return t('{count} memory items ready').replace('{count}', String(memories.value.length));
});

const activePresetTitle = computed(() => {
  return selectedPreset.value?.name || t('Quick launch');
});

const activePresetDescription = computed(() => {
  return selectedPreset.value?.description || t('Start from your defaults and route the task into the right workspace.');
});

const activeWorkspaceLabel = computed(() => {
  return activeWorkspace.value?.name || t('Personal Inbox');
});

const activeInstructionsPreview = computed(() => {
  if (selectedPreset.value?.instructions) {
    return selectedPreset.value.instructions;
  }
  return t('No preset instructions applied. Forge will use your saved model defaults and general system behavior.');
});

const showUserMenu = ref(false);
const userMenuTimeout = ref<ReturnType<typeof setTimeout> | null>(null);

const syncModelInputs = (preset: AgentPreset | null) => {
  const defaults = forgeProfile.value.model_preferences;
  selectedModelProvider.value = preset?.model_provider || defaults.model_provider;
  selectedModelName.value = preset?.model_name || defaults.model_name;
  selectedTemperature.value = preset?.temperature ?? defaults.temperature;
  selectedMaxTokens.value = preset?.max_tokens ?? defaults.max_tokens;

  if (preset?.workspace_id && workspaces.value.some((workspace) => workspace.id === preset.workspace_id)) {
    selectedWorkspaceId.value = preset.workspace_id;
  }
};

const handleUserMenuEnter = () => {
  if (userMenuTimeout.value) {
    clearTimeout(userMenuTimeout.value);
    userMenuTimeout.value = null;
  }
  showUserMenu.value = true;
};

const handleUserMenuLeave = () => {
  userMenuTimeout.value = setTimeout(() => {
    showUserMenu.value = false;
  }, 200);
};

watch(
  () => forgeProfile.value,
  () => {
    if (!selectedPresetId.value) {
      syncModelInputs(null);
    }
  },
  { immediate: true, deep: true }
);

watch(selectedPreset, (preset) => {
  syncModelInputs(preset);
});

onMounted(() => {
  hideFilePanel();
});

onMounted(async () => {
  const clientConfig = await getCachedClientConfig();
  if (clientConfig) {
    showGithubButton.value = clientConfig.show_github_button;
    githubRepositoryUrl.value = clientConfig.github_repository_url;
  }
});

const handleSubmit = async () => {
  if (!message.value.trim() || isSubmitting.value) {
    return;
  }

  isSubmitting.value = true;

  try {
    const fallbackPreferences = forgeProfile.value.model_preferences;
    const session = await createSession({
      workspace_id: selectedWorkspaceId.value || undefined,
      preset_id: selectedPresetId.value || undefined,
      model_provider: selectedModelProvider.value.trim(),
      model_name: selectedModelName.value.trim(),
      temperature: Number.isFinite(Number(selectedTemperature.value))
        ? Number(selectedTemperature.value)
        : fallbackPreferences.temperature,
      max_tokens: Number.isFinite(Number(selectedMaxTokens.value))
        ? Number(selectedMaxTokens.value)
        : fallbackPreferences.max_tokens,
    });
    const sessionId = session.session_id;

    router.push({
      path: `/chat/${sessionId}`,
      state: {
        message: message.value,
        files: attachments.value.map((file: FileInfo) => ({
          file_id: file.file_id,
          filename: file.filename,
          content_type: file.content_type,
          size: file.size,
          upload_date: file.upload_date,
        })),
      },
    });
  } catch (error) {
    console.error('Failed to create session:', error);
    showErrorToast(t('Failed to create agent, please try again later'));
    isSubmitting.value = false;
  }
};
</script>

<style scoped>
.studio-input {
  width: 100%;
  min-height: 40px;
  border-radius: 14px;
  border: 1px solid var(--border-main);
  background: var(--background-menu-white);
  padding: 0 14px;
  color: var(--text-primary);
  font-size: 14px;
  line-height: 20px;
}

.studio-input:focus {
  outline: 1.5px solid var(--border-dark);
  outline-offset: 0;
}
</style>
