<template>
  <SimpleBar>
    <div
      class="flex flex-col h-full flex-1 min-w-0 mx-auto w-full sm:min-w-[390px] px-5 justify-center items-start gap-2 relative max-w-full sm:max-w-full">
      <div class="w-full pt-4 pb-4 px-5 bg-[var(--background-gray-main)] sticky top-0 z-10 mx-[-1.25]">
        <div class="flex justify-between items-center w-full absolute left-0 right-0">
          <div class="h-8 relative z-20 overflow-hidden flex gap-2 items-center flex-shrink-0">
            <div class="relative flex items-center">
              <div @click="toggleLeftPanel" v-if="!isLeftPanelShow"
                class="flex h-7 w-7 items-center justify-center cursor-pointer rounded-md hover:bg-[var(--fill-tsp-gray-main)]">
                <PanelLeft class="size-5 text-[var(--icon-secondary)]" />
              </div>
            </div>
            <button class="flex items-center gap-2 h-9 px-3 rounded-full border border-[var(--border-btn-main)] bg-[var(--background-white-main)]" @click="showVersionToast">
              <Bot :size="18" />
              <span class="text-sm font-medium text-[var(--text-primary)]">Forge</span>
              <ChevronDown :size="14" class="text-[var(--icon-secondary)]" />
            </button>
            <div class="hidden sm:flex items-center gap-2 ml-4">
              <button
                @click="selectedModelTier = 'regular'"
                class="h-8 px-3 rounded-full border text-sm"
                :class="selectedModelTier === 'regular' ? 'bg-black text-white border-black' : 'bg-transparent text-[var(--text-secondary)] border-[var(--border-btn-main)]'">
                Regular
              </button>
              <button
                @click="selectedModelTier = 'max'"
                class="h-8 px-3 rounded-full border text-sm"
                :class="selectedModelTier === 'max' ? 'bg-black text-white border-black' : 'bg-transparent text-[var(--text-secondary)] border-[var(--border-btn-main)]'">
                Max
              </button>
            </div>
          </div>
          <div class="flex items-center gap-2">
            <button
              class="hidden sm:flex h-8 w-8 items-center justify-center rounded-full border border-[var(--border-btn-main)] bg-[var(--background-white-main)] text-[var(--text-secondary)]"
              @click="showInfoToast('No notifications yet')">
              <Bell :size="16" />
            </button>
            <span
              class="hidden sm:flex h-8 px-3 rounded-full border text-sm items-center gap-2 border-[var(--border-btn-main)] bg-[var(--background-white-main)] text-[var(--text-secondary)]">
              <span class="inline-flex h-2 w-2 rounded-full bg-black"></span>
              {{ currentUser?.credits ?? '...' }} credits
            </span>
            <button
              class="hidden sm:flex h-8 w-8 items-center justify-center rounded-full border border-[var(--border-btn-main)] bg-[var(--background-white-main)] text-[var(--text-secondary)]"
              @click="showInfoToast('Multi-account support coming soon')">
              <Plus :size="16" />
            </button>
            <div class="relative flex items-center" aria-expanded="false" aria-haspopup="dialog"
              @mouseenter="handleUserMenuEnter" @mouseleave="handleUserMenuLeave">
              <div class="relative flex items-center justify-center font-bold cursor-pointer flex-shrink-0">
                <div
                  class="relative flex items-center justify-center font-bold flex-shrink-0 rounded-full overflow-hidden"
                  style="width: 32px; height: 32px; font-size: 16px; color: rgba(255, 255, 255, 0.9); background-color: rgb(59, 130, 246);">
                  {{ avatarLetter }}</div>
              </div>
              <!-- User Menu -->
              <div v-if="showUserMenu" @mouseenter="handleUserMenuEnter" @mouseleave="handleUserMenuLeave"
                class="absolute top-full right-0 mt-1 mr-[-15px] z-50">
                <UserMenu />
              </div>
            </div>
          </div>
        </div>
        <div class="h-8"></div>
      </div>
      <div class="w-full max-w-full sm:max-w-[768px] sm:min-w-[390px] mx-auto mt-[180px] mb-auto">
        <div class="w-full flex pl-4 items-center justify-start pb-4">
          <span class="text-[var(--text-primary)] text-start font-serif text-[32px] leading-[40px]" :style="{
            fontFamily:
              'ui-serif, Georgia, Cambria, &quot;Times New Roman&quot;, Times, serif',
          }">
            {{ $t('Hello') }}, <span v-text="currentUser?.fullname || 'User'"></span>
            <br />
            <span class="text-[var(--text-tertiary)]">
              {{ $t('What can I do for you?') }}
            </span>
          </span>
        </div>
        <div class="flex flex-col gap-1 w-full">
          <div class="flex flex-wrap items-center gap-2 pl-1 pb-3">
            <button
              @click="selectedMode = 'auto'"
              class="h-8 px-3 rounded-full border text-sm"
              :class="selectedMode === 'auto' ? 'bg-black text-white border-black' : 'bg-transparent text-[var(--text-secondary)] border-[var(--border-btn-main)]'">
              Auto
            </button>
            <button
              @click="selectedMode = 'checkpoint'"
              class="h-8 px-3 rounded-full border text-sm"
              :class="selectedMode === 'checkpoint' ? 'bg-black text-white border-black' : 'bg-transparent text-[var(--text-secondary)] border-[var(--border-btn-main)]'">
              Checkpoint
            </button>
            <select v-model="selectedBudget"
              class="h-8 px-3 rounded-full border text-sm bg-[var(--background-white-main)] border-[var(--border-btn-main)] text-[var(--text-secondary)]">
              <option :value="8">Budget 8</option>
              <option :value="16">Budget 16</option>
              <option :value="32">Budget 32</option>
            </select>
            <select v-model="selectedPermissions"
              class="h-8 px-3 rounded-full border text-sm bg-[var(--background-white-main)] border-[var(--border-btn-main)] text-[var(--text-secondary)]">
              <option value="standard">Standard Access</option>
              <option value="guarded">Guarded Access</option>
            </select>
          </div>
          <div class="flex flex-col bg-[var(--background-gray-main)] w-full">
            <div class="[&amp;:not(:empty)]:pb-2 bg-[var(--background-gray-main)] rounded-[22px_22px_0px_0px]">
            </div>
            <ChatBox :rows="2" v-model="message" @submit="handleSubmit" :isRunning="false" :attachments="attachments" :disabled="(currentUser?.credits ?? 0) <= 0" />
          </div>
        </div>
      </div>
    </div>
  </SimpleBar>
</template>

<script setup lang="ts">
import SimpleBar from '../components/SimpleBar.vue';
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';
import ChatBox from '../components/ChatBox.vue';
import { createSession } from '../api/agent';
import { showErrorToast, showInfoToast } from '../utils/toast';
import { Bot, PanelLeft, ChevronDown, Bell, Plus } from 'lucide-vue-next';
import type { FileInfo } from '../api/file';
import { useLeftPanel } from '../composables/useLeftPanel';
import { useFilePanel } from '../composables/useFilePanel';
import { useAuth } from '../composables/useAuth';
import { getCachedClientConfig } from '../api/config';
import UserMenu from '../components/UserMenu.vue';

const { t } = useI18n();
const router = useRouter();
const message = ref('');
const isSubmitting = ref(false);
const attachments = ref<FileInfo[]>([]);
const { toggleLeftPanel, isLeftPanelShow } = useLeftPanel();
const { hideFilePanel } = useFilePanel();
const { currentUser } = useAuth();
const selectedModelTier = ref<'regular' | 'max'>((localStorage.getItem('forge-model-tier') as 'regular' | 'max') || 'regular');
const selectedMode = ref<'auto' | 'checkpoint'>((localStorage.getItem('forge-run-mode') as 'auto' | 'checkpoint') || 'auto');
const selectedBudget = ref(Number(localStorage.getItem('forge-run-budget') || '16'));
const selectedPermissions = ref<'standard' | 'guarded'>((localStorage.getItem('forge-run-permissions') as 'standard' | 'guarded') || 'standard');
const showVersionToast = () => showInfoToast('Forge version picker coming soon');

// Get first letter of user's fullname for avatar display
const avatarLetter = computed(() => {
  return currentUser.value?.fullname?.charAt(0)?.toUpperCase() || 'F';
});

// User menu state
const showUserMenu = ref(false);
const userMenuTimeout = ref<number | null>(null);

// Show user menu on hover
const handleUserMenuEnter = () => {
  if (userMenuTimeout.value) {
    clearTimeout(userMenuTimeout.value);
    userMenuTimeout.value = null;
  }
  showUserMenu.value = true;
};

// Hide user menu with delay
const handleUserMenuLeave = () => {
  userMenuTimeout.value = setTimeout(() => {
    showUserMenu.value = false;
  }, 200); // 200ms delay to allow moving to menu
};

onMounted(() => {
  hideFilePanel();
})

const handleSubmit = async () => {
  if (message.value.trim() && !isSubmitting.value) {
    isSubmitting.value = true;

    try {
      // Create new Agent
      localStorage.setItem('forge-model-tier', selectedModelTier.value);
      localStorage.setItem('forge-run-mode', selectedMode.value);
      localStorage.setItem('forge-run-budget', String(selectedBudget.value));
      localStorage.setItem('forge-run-permissions', selectedPermissions.value);
      const session = await createSession(selectedModelTier.value, message.value, {
        maxBudget: selectedBudget.value,
        mode: selectedMode.value,
        permissions: selectedPermissions.value,
      });
      if (currentUser.value) {
        currentUser.value.credits = Math.max(0, (currentUser.value.credits ?? 0) - (session.spent_credits ?? session.estimated_cost ?? 0));
      }
      const sessionId = session.session_id;

      // Navigate to new route with session_id, passing initial message via state
      router.push({
        path: `/chat/${sessionId}`,
        state: {
          message: message.value, files: attachments.value.map((file: FileInfo) => ({
            file_id: file.file_id,
            filename: file.filename,
            content_type: file.content_type,
            size: file.size,
            upload_date: file.upload_date
          }))
        }
      });
    } catch (error) {
      console.error('Failed to create session:', error);
      showErrorToast((error as any)?.response?.data?.msg || t('Failed to create session, please try again later'));
      isSubmitting.value = false;
      // Note: Don't clear message/attachments to allow user to retry
    }
  }
};
</script>
