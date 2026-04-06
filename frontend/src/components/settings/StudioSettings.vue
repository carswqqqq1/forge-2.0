<template>
  <div class="flex flex-col gap-8 w-full">
    <section class="settings-section">
      <div class="settings-title">{{ t('Model Defaults') }}</div>
      <div class="settings-description">
        {{ t('These values become the starting point for new tasks unless a preset overrides them.') }}
      </div>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
        <label class="settings-field">
          <span>{{ t('Model Provider') }}</span>
          <input v-model="profile.model_preferences.model_provider" class="settings-input" type="text" />
        </label>
        <label class="settings-field">
          <span>{{ t('Model Name') }}</span>
          <input v-model="profile.model_preferences.model_name" class="settings-input" type="text" />
        </label>
        <label class="settings-field">
          <span>{{ t('Temperature') }}</span>
          <input v-model.number="profile.model_preferences.temperature" class="settings-input" type="number" min="0" max="1" step="0.1" />
        </label>
        <label class="settings-field">
          <span>{{ t('Max Tokens') }}</span>
          <input v-model.number="profile.model_preferences.max_tokens" class="settings-input" type="number" min="256" step="256" />
        </label>
      </div>
    </section>

    <section class="settings-section">
      <div class="flex items-center justify-between gap-3">
        <div class="flex flex-col gap-1">
          <div class="settings-title">{{ t('Workspaces') }}</div>
          <div class="settings-description">
            {{ t('Group sessions by client, project, or operating lane.') }}
          </div>
        </div>
        <button class="secondary-button" @click="addWorkspace">{{ t('Add Workspace') }}</button>
      </div>

      <div class="flex flex-col gap-4 mt-4">
        <div v-if="profile.workspaces.length === 0" class="empty-state">
          {{ t('No workspaces yet. Create one to organize related sessions.') }}
        </div>
        <div v-for="workspace in profile.workspaces" :key="workspace.id" class="editor-card">
          <div class="grid grid-cols-1 md:grid-cols-[1fr_1fr_120px_auto] gap-3 items-start">
            <label class="settings-field">
              <span>{{ t('Name') }}</span>
              <input v-model="workspace.name" class="settings-input" type="text" />
            </label>
            <label class="settings-field">
              <span>{{ t('Description') }}</span>
              <input v-model="workspace.description" class="settings-input" type="text" />
            </label>
            <label class="settings-field">
              <span>{{ t('Color') }}</span>
              <input v-model="workspace.color" class="settings-input settings-color" type="color" />
            </label>
            <button class="danger-button mt-6" @click="removeWorkspace(workspace.id)">
              {{ t('Delete') }}
            </button>
          </div>
        </div>
      </div>
    </section>

    <section class="settings-section">
      <div class="flex items-center justify-between gap-3">
        <div class="flex flex-col gap-1">
          <div class="settings-title">{{ t('Memories') }}</div>
          <div class="settings-description">
            {{ t('Pin recurring context Forge should keep in mind across future work.') }}
          </div>
        </div>
        <button class="secondary-button" @click="addMemory">{{ t('Add Memory') }}</button>
      </div>

      <div class="flex flex-col gap-4 mt-4">
        <div v-if="profile.memories.length === 0" class="empty-state">
          {{ t('No saved memory yet. Add team facts, preferences, or recurring context here.') }}
        </div>
        <div v-for="memory in profile.memories" :key="memory.id" class="editor-card">
          <div class="flex flex-col gap-3">
            <textarea v-model="memory.content" class="settings-textarea" rows="3"></textarea>
            <div class="flex justify-end">
              <button class="danger-button" @click="removeMemory(memory.id)">{{ t('Delete') }}</button>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="settings-section">
      <div class="flex items-center justify-between gap-3">
        <div class="flex flex-col gap-1">
          <div class="settings-title">{{ t('Agent Presets') }}</div>
          <div class="settings-description">
            {{ t('Create reusable launch profiles with instructions, model settings, and a default workspace.') }}
          </div>
        </div>
        <button class="secondary-button" @click="addPreset">{{ t('Add Preset') }}</button>
      </div>

      <div class="flex flex-col gap-4 mt-4">
        <div v-if="profile.agent_presets.length === 0" class="empty-state">
          {{ t('No presets yet. Add one for research, coding, operations, or client-specific work.') }}
        </div>
        <div v-for="preset in profile.agent_presets" :key="preset.id" class="editor-card">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <label class="settings-field">
              <span>{{ t('Name') }}</span>
              <input v-model="preset.name" class="settings-input" type="text" />
            </label>
            <label class="settings-field">
              <span>{{ t('Workspace') }}</span>
              <select v-model="preset.workspace_id" class="settings-input">
                <option :value="null">{{ t('None') }}</option>
                <option v-for="workspace in profile.workspaces" :key="workspace.id" :value="workspace.id">
                  {{ workspace.name }}
                </option>
              </select>
            </label>
            <label class="settings-field md:col-span-2">
              <span>{{ t('Description') }}</span>
              <input v-model="preset.description" class="settings-input" type="text" />
            </label>
            <label class="settings-field md:col-span-2">
              <span>{{ t('Instructions') }}</span>
              <textarea v-model="preset.instructions" class="settings-textarea" rows="4"></textarea>
            </label>
            <label class="settings-field">
              <span>{{ t('Model Provider') }}</span>
              <input v-model="preset.model_provider" class="settings-input" type="text" />
            </label>
            <label class="settings-field">
              <span>{{ t('Model Name') }}</span>
              <input v-model="preset.model_name" class="settings-input" type="text" />
            </label>
            <label class="settings-field">
              <span>{{ t('Temperature') }}</span>
              <input v-model.number="preset.temperature" class="settings-input" type="number" min="0" max="1" step="0.1" />
            </label>
            <label class="settings-field">
              <span>{{ t('Max Tokens') }}</span>
              <input v-model.number="preset.max_tokens" class="settings-input" type="number" min="256" step="256" />
            </label>
          </div>
          <div class="flex justify-end mt-4">
            <button class="danger-button" @click="removePreset(preset.id)">{{ t('Delete') }}</button>
          </div>
        </div>
      </div>
    </section>

    <div class="flex items-center justify-between gap-3 sticky bottom-0 bg-[var(--background-menu-white)] pt-2">
      <div class="text-[13px] text-[var(--text-tertiary)]">
        {{ dirty ? t('Studio changes are ready to save.') : t('Studio is up to date.') }}
      </div>
      <div class="flex items-center gap-3">
        <button class="secondary-button" :disabled="isSaving" @click="resetLocalState">{{ t('Reset') }}</button>
        <button class="primary-button" :disabled="isSaving || !dirty" @click="saveProfile">
          {{ isSaving ? t('Saving...') : t('Save Studio') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import {
  type ForgeProfile,
  updateForgeProfile,
} from '@/api/auth';
import { useAuth } from '@/composables/useAuth';
import { showErrorToast, showSuccessToast } from '@/utils/toast';

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
const { currentUser, loadCurrentUser } = useAuth();

const profile = ref<ForgeProfile>(JSON.parse(JSON.stringify(DEFAULT_FORGE_PROFILE)));
const initialSerializedProfile = ref(JSON.stringify(DEFAULT_FORGE_PROFILE));
const isSaving = ref(false);

const dirty = computed(() => JSON.stringify(profile.value) !== initialSerializedProfile.value);

const syncFromUser = () => {
  const nextProfile = currentUser.value?.forge_profile || DEFAULT_FORGE_PROFILE;
  profile.value = JSON.parse(JSON.stringify(nextProfile));
  initialSerializedProfile.value = JSON.stringify(profile.value);
};

watch(() => currentUser.value?.forge_profile, syncFromUser, { immediate: true, deep: true });

const addWorkspace = () => {
  profile.value.workspaces.push({
    id: crypto.randomUUID().replace(/-/g, '').slice(0, 12),
    name: '',
    description: '',
    color: '#0ea5e9',
  });
};

const removeWorkspace = (workspaceId: string) => {
  profile.value.workspaces = profile.value.workspaces.filter((workspace) => workspace.id !== workspaceId);
  profile.value.agent_presets = profile.value.agent_presets.map((preset) => (
    preset.workspace_id === workspaceId ? { ...preset, workspace_id: null } : preset
  ));
};

const addMemory = () => {
  profile.value.memories.push({
    id: crypto.randomUUID().replace(/-/g, '').slice(0, 12),
    content: '',
  });
};

const removeMemory = (memoryId: string) => {
  profile.value.memories = profile.value.memories.filter((memory) => memory.id !== memoryId);
};

const addPreset = () => {
  profile.value.agent_presets.push({
    id: crypto.randomUUID().replace(/-/g, '').slice(0, 12),
    name: '',
    description: '',
    instructions: '',
    model_provider: profile.value.model_preferences.model_provider,
    model_name: profile.value.model_preferences.model_name,
    temperature: profile.value.model_preferences.temperature,
    max_tokens: profile.value.model_preferences.max_tokens,
    workspace_id: profile.value.workspaces[0]?.id || null,
  });
};

const removePreset = (presetId: string) => {
  profile.value.agent_presets = profile.value.agent_presets.filter((preset) => preset.id !== presetId);
};

const resetLocalState = () => {
  syncFromUser();
};

const saveProfile = async () => {
  isSaving.value = true;
  try {
    const updatedProfile = await updateForgeProfile({ forge_profile: profile.value });
    profile.value = JSON.parse(JSON.stringify(updatedProfile));
    initialSerializedProfile.value = JSON.stringify(profile.value);
    await loadCurrentUser();
    showSuccessToast(t('Studio settings saved'));
  } catch (error: any) {
    console.error('Failed to save Forge profile:', error);
    showErrorToast(error?.response?.data?.message || error?.message || t('Failed to save studio settings'));
  } finally {
    isSaving.value = false;
  }
};
</script>

<style scoped>
.settings-section {
  width: 100%;
  padding-bottom: 24px;
  border-bottom: 1px solid var(--border-light);
}

.settings-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
}

.settings-description {
  font-size: 13px;
  line-height: 22px;
  color: var(--text-tertiary);
}

.settings-field {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.settings-field span {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary);
}

.settings-input,
.settings-textarea {
  width: 100%;
  border-radius: 14px;
  border: 1px solid var(--border-main);
  background: var(--background-menu-white);
  color: var(--text-primary);
  padding: 0 14px;
  font-size: 14px;
  line-height: 20px;
}

.settings-input {
  min-height: 40px;
}

.settings-color {
  padding: 6px;
}

.settings-textarea {
  min-height: 96px;
  padding-top: 12px;
  padding-bottom: 12px;
  resize: vertical;
}

.editor-card {
  border-radius: 18px;
  border: 1px solid var(--border-light);
  background: var(--fill-tsp-white-main);
  padding: 16px;
}

.empty-state {
  border-radius: 18px;
  border: 1px dashed var(--border-main);
  color: var(--text-tertiary);
  font-size: 13px;
  line-height: 22px;
  padding: 18px;
}

.primary-button,
.secondary-button,
.danger-button {
  height: 36px;
  border-radius: 10px;
  padding: 0 14px;
  font-size: 14px;
  font-weight: 500;
  transition: opacity 0.2s ease;
}

.primary-button {
  background: var(--Button-primary-black);
  color: var(--text-onblack);
}

.secondary-button {
  border: 1px solid var(--border-btn-main);
  color: var(--text-primary);
  background: transparent;
}

.danger-button {
  border: 1px solid rgba(220, 38, 38, 0.25);
  color: rgb(185, 28, 28);
  background: rgba(254, 242, 242, 0.9);
}

.primary-button:disabled,
.secondary-button:disabled,
.danger-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
