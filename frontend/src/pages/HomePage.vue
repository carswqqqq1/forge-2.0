<template>
  <SimpleBar>
    <div class="flex flex-col h-full flex-1 min-w-0 mx-auto w-full px-5 relative max-w-full bg-[var(--background-gray-main)]">
      <div class="w-full pt-4 pb-4 px-5 sticky top-0 z-10 mx-[-1.25rem] bg-[var(--background-gray-main)]">
        <div class="flex justify-between items-center w-full">
          <div class="flex items-center gap-2">
            <div @click="toggleLeftPanel" v-if="!isLeftPanelShow" class="flex h-7 w-7 items-center justify-center cursor-pointer rounded-md hover:bg-[var(--fill-tsp-gray-main)]">
              <PanelLeft class="size-5 text-[var(--icon-secondary)]" />
            </div>
            <ForgeModelDropdown />
          </div>

          <div class="flex items-center gap-2">
            <span class="hidden sm:flex h-8 px-3 rounded-full border text-sm items-center gap-2 border-[var(--border-btn-main)] bg-[var(--background-white-main)] text-[var(--text-secondary)]">
              <Sparkles :size="14" />
              {{ currentUser?.credits ?? '...' }}
            </span>
            <button class="hidden sm:flex h-8 w-8 items-center justify-center rounded-full border border-[var(--border-btn-main)] bg-[var(--background-white-main)] text-[var(--text-secondary)]" @click="showInfoToast('No notifications yet')">
              <Bell :size="16" />
            </button>
            <button class="hidden sm:flex h-8 w-8 items-center justify-center rounded-full border border-[var(--border-btn-main)] bg-[var(--background-white-main)] text-[var(--text-secondary)]" @click="showInfoToast('Multi-account support coming soon')">
              <Plus :size="16" />
            </button>
            <div class="relative flex items-center gap-2" aria-expanded="false" aria-haspopup="dialog" @mouseenter="handleUserMenuEnter" @mouseleave="handleUserMenuLeave">
              <div class="relative flex items-center justify-center font-bold flex-shrink-0 rounded-full overflow-hidden" style="width: 32px; height: 32px; font-size: 16px; color: rgba(255, 255, 255, 0.9); background-color: rgb(59, 130, 246);">
                {{ avatarLetter }}
              </div>
              <div v-if="showUserMenu" @mouseenter="handleUserMenuEnter" @mouseleave="handleUserMenuLeave" class="absolute top-full right-0 mt-1 mr-[-15px] z-50">
                <UserMenu />
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="w-full max-w-[820px] mx-auto pt-14 pb-10">
        <div class="text-center mb-10">
          <h1 class="forge-home-heading">What can I do for you?</h1>
        </div>

        <ChatBox
          :rows="2"
          v-model="message"
          @submit="handleSubmit"
          :isRunning="false"
          :attachments="attachments"
          :disabled="(currentUser?.credits ?? 0) <= 0"
          :placeholder="wideResearch ? 'What topic do you want to research deeply?' : 'Assign a task to Forge...'" />

        <div class="mt-4 flex flex-wrap items-center justify-center gap-2">
          <button v-for="action in primaryActions" :key="action.label" class="quick-pill" @click="applyQuickAction(action)">
            <component :is="action.icon" :size="14" />
            <span>{{ action.label }}</span>
          </button>
          <div class="relative">
            <button class="quick-pill" @click="showMore = !showMore">
              <span>More</span>
            </button>
            <div v-if="showMore" class="absolute top-full right-0 mt-2 w-[220px] rounded-[18px] border border-[var(--border-main)] bg-white shadow-[0px_18px_48px_0px_rgba(0,0,0,0.12)] p-2 z-50">
              <button v-for="action in moreActions" :key="action.label" class="more-action" @click="applyQuickAction(action)">
                <div class="flex items-center gap-2 min-w-0">
                  <component :is="action.icon" :size="14" />
                  <span class="truncate">{{ action.label }}</span>
                </div>
                <ExternalLink v-if="action.external" :size="14" />
              </button>
            </div>
          </div>
        </div>

        <div v-if="!onboardingDismissed" class="mt-12">
          <div class="rounded-[26px] border border-[var(--border-main)] bg-white p-5 shadow-[0px_14px_40px_0px_rgba(0,0,0,0.05)]">
            <div class="flex items-start justify-between gap-4">
              <div>
                <div class="text-[18px] font-semibold text-[var(--text-primary)]">{{ onboardingCards[onboardingIndex].title }}</div>
                <div class="mt-2 text-[14px] leading-7 text-[var(--text-secondary)]">{{ onboardingCards[onboardingIndex].description }}</div>
              </div>
              <button class="h-8 w-8 rounded-full hover:bg-[var(--fill-tsp-white-light)] flex items-center justify-center" @click="dismissOnboarding">
                <X :size="16" class="text-[var(--icon-secondary)]" />
              </button>
            </div>
            <div class="mt-6 flex items-center justify-between">
              <div class="flex items-center gap-2">
                <button v-for="(_, idx) in onboardingCards" :key="idx" class="h-2.5 rounded-full transition-all" :class="idx === onboardingIndex ? 'w-6 bg-[var(--text-primary)]' : 'w-2.5 bg-black/15'" @click="onboardingIndex = idx"></button>
              </div>
              <button class="rounded-full border border-[var(--border-main)] px-4 py-2 text-sm font-medium" @click="nextOnboardingCard">
                Next
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </SimpleBar>
</template>

<script setup lang="ts">
import SimpleBar from '../components/SimpleBar.vue';
import { computed, onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import ChatBox from '../components/ChatBox.vue';
import { createSession } from '../api/agent';
import { showErrorToast, showInfoToast } from '../utils/toast';
import { PanelLeft, Sparkles, Plus, Bell, BriefcaseBusiness, Monitor, Laptop, PenTool, AppWindow, CalendarClock, SearchCheck, Sheet, ChartColumn, Clapperboard, AudioWaveform, MessageCircle, ExternalLink, X } from 'lucide-vue-next';
import type { FileInfo } from '../api/file';
import { useLeftPanel } from '../composables/useLeftPanel';
import { useFilePanel } from '../composables/useFilePanel';
import { useAuth } from '../composables/useAuth';
import UserMenu from '../components/UserMenu.vue';
import ForgeModelDropdown from '../components/ForgeModelDropdown.vue';
import { useModelTier } from '../composables/useModelTier';

type QuickAction = {
  label: string;
  icon: any;
  prompt: string;
  wideResearch?: boolean;
  external?: boolean;
};

const router = useRouter();
const message = ref('');
const isSubmitting = ref(false);
const attachments = ref<FileInfo[]>([]);
const { toggleLeftPanel, isLeftPanelShow } = useLeftPanel();
const { hideFilePanel } = useFilePanel();
const { currentUser } = useAuth();
const { currentTier } = useModelTier();
const showMore = ref(false);
const wideResearch = ref(false);

const avatarLetter = computed(() => currentUser.value?.fullname?.charAt(0)?.toUpperCase() || 'F');
const showUserMenu = ref(false);
const userMenuTimeout = ref<number | null>(null);
const onboardingDismissed = ref(localStorage.getItem('forge-onboarding-dismissed') === 'true');
const onboardingIndex = ref(0);

const primaryActions: QuickAction[] = [
  { label: 'Create slides', icon: BriefcaseBusiness, prompt: 'Create a presentation about ' },
  { label: 'Build website', icon: Monitor, prompt: 'Build a website for ' },
  { label: 'Develop desktop apps', icon: Laptop, prompt: 'Develop a desktop app that ' },
  { label: 'Design', icon: PenTool, prompt: 'Design a concept for ' },
];

const moreActions: QuickAction[] = [
  { label: 'Develop apps', icon: AppWindow, prompt: 'Develop an app that ' },
  { label: 'Schedule task', icon: CalendarClock, prompt: 'Schedule a task that ' },
  { label: 'Wide Research', icon: SearchCheck, prompt: 'Conduct deep research on ', wideResearch: true },
  { label: 'Spreadsheet', icon: Sheet, prompt: 'Create a spreadsheet for ' },
  { label: 'Visualization', icon: ChartColumn, prompt: 'Create a visualization for ' },
  { label: 'Video', icon: Clapperboard, prompt: 'Create a video plan for ' },
  { label: 'Audio', icon: AudioWaveform, prompt: 'Create an audio brief for ' },
  { label: 'Chat mode', icon: MessageCircle, prompt: 'Help me think through ' },
  { label: 'Playbook', icon: ExternalLink, prompt: 'Create a playbook for ', external: true },
];

const onboardingCards = [
  {
    title: 'Get the most out of Forge',
    description: 'Tell Forge about your preferences, workflows, and how you like tasks to be handled so it can stay aligned across runs.',
  },
  {
    title: 'Connect your tools',
    description: 'Link GitHub, Gmail, Calendar, and more so Forge can do deeper work with your real systems and context.',
  },
  {
    title: 'Wide research mode',
    description: 'Use Wide Research when you want Forge to break a topic into subtopics, search broadly, and synthesize a full report.',
  },
];

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

const applyQuickAction = (action: QuickAction) => {
  message.value = action.prompt;
  wideResearch.value = !!action.wideResearch;
  showMore.value = false;
};

const dismissOnboarding = () => {
  onboardingDismissed.value = true;
  localStorage.setItem('forge-onboarding-dismissed', 'true');
};

const nextOnboardingCard = () => {
  onboardingIndex.value = (onboardingIndex.value + 1) % onboardingCards.length;
};

onMounted(() => {
  hideFilePanel();
});

const handleSubmit = async () => {
  if (message.value.trim() && !isSubmitting.value) {
    isSubmitting.value = true;
    try {
      const session = await createSession(currentTier.value, message.value, {
        maxBudget: currentTier.value === 'max' ? 32 : currentTier.value === 'regular' ? 20 : 12,
        mode: 'auto',
        permissions: 'standard',
        wideResearch: wideResearch.value,
      });
      if (currentUser.value) {
        currentUser.value.credits = Math.max(0, (currentUser.value.credits ?? 0) - (session.spent_credits ?? session.estimated_cost ?? 0));
      }
      router.push({
        path: `/chat/${session.session_id}`,
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
      showErrorToast((error as any)?.response?.data?.msg || 'Failed to create session, please try again later');
      isSubmitting.value = false;
      return;
    }
  }
};
</script>

<style scoped>
.forge-home-heading {
  font-family: 'Georgia', 'Times New Roman', serif;
  font-size: 40px;
  font-weight: 400;
  color: #1a1a1a;
  line-height: 1.15;
}

.quick-pill {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  border-radius: 9999px;
  border: 1px solid #e5e7eb;
  background: white;
  padding: 8px 16px;
  font-size: 13px;
  color: var(--text-secondary);
}

.quick-pill:hover,
.more-action:hover {
  background: var(--background-gray-main);
}

.more-action {
  width: 100%;
  height: 38px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-radius: 12px;
  padding: 0 12px;
  font-size: 13px;
  color: var(--text-primary);
}
</style>
