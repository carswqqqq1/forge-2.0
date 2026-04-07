<template>
  <SimpleBar ref="simpleBarRef" @scroll="handleScroll">
    <div ref="chatContainerRef" class="relative flex flex-col h-full flex-1 min-w-0 px-5 bg-[var(--background-gray-main)]">
      <div ref="observerRef" class="sm:min-w-[390px] flex flex-row items-center justify-between pt-3 pb-2 gap-3 sticky top-0 z-10 bg-[var(--background-gray-main)] flex-shrink-0">
        <div class="flex items-center flex-1">
          <div class="relative flex items-center">
            <div @click="toggleLeftPanel" v-if="!isLeftPanelShow" class="flex h-7 w-7 items-center justify-center cursor-pointer rounded-md hover:bg-[var(--fill-tsp-gray-main)]">
              <PanelLeft class="size-5 text-[var(--icon-secondary)]" />
            </div>
          </div>
        </div>

        <div class="max-w-full sm:max-w-[820px] sm:min-w-[390px] flex w-full flex-col gap-[6px] overflow-hidden">
          <div class="flex items-center justify-between gap-3 min-w-0">
            <div class="flex items-center gap-3 min-w-0">
              <ForgeModelDropdown />
              <span class="whitespace-nowrap text-ellipsis overflow-hidden text-[22px] font-medium text-[var(--text-primary)]">
                {{ title || 'New task' }}
              </span>
            </div>
            <div class="flex items-center gap-2 flex-shrink-0">
              <CreditsPopover />
              <button class="header-action-btn hidden sm:inline-flex" @click="showInfoToast('Collaboration is coming soon')">
                <UsersRound :size="15" />
                <span>Collaborate</span>
              </button>
              <button class="header-action-btn" @click="handleCopyLink">
                <Share2 :size="15" />
                <span>Share</span>
              </button>
              <button class="icon-header-btn" @click="handleExport">
                <Download :size="16" />
              </button>
              <div class="relative">
                <button class="icon-header-btn" @click="showOverflow = !showOverflow">
                  <MoreHorizontal :size="16" />
                </button>
                <div v-if="showOverflow" class="absolute top-full right-0 mt-2 w-[180px] rounded-[16px] border border-[var(--border-main)] bg-white shadow-[0px_18px_48px_0px_rgba(0,0,0,0.12)] p-2 z-40">
                  <button class="overflow-action" @click="renameCurrentTask">Rename task</button>
                  <button class="overflow-action" @click="handleCopyLink">Share link</button>
                  <button class="overflow-action text-[#dc2626]" @click="deleteCurrentTask">Delete task</button>
                </div>
              </div>
            </div>
          </div>

          <div class="flex flex-wrap items-center gap-2">
            <span class="run-pill">{{ runModeLabel }}</span>
            <span class="run-pill">Budget {{ spentCredits }}/{{ maxBudget }}</span>
            <span class="run-pill">{{ permissionsLabel }}</span>
            <span class="run-pill">{{ riskLabel }}</span>
          </div>
        </div>
        <div class="flex-1"></div>
      </div>

      <div class="mx-auto w-full max-w-full sm:max-w-[820px] sm:min-w-[390px] flex flex-col flex-1">
        <div class="flex flex-col w-full gap-[12px] pb-[80px] pt-[12px] flex-1 overflow-y-auto">
          <WideResearchCard
            v-if="wideResearchSubjects.length > 0"
            :title="title || goal || 'your topic'"
            :subjects="wideResearchSubjects"
            :completed="wideResearchCompleted"
            :total="wideResearchSubjects.length"
            :started="wideResearchStarted"
            :showSkip="showWideResearchSkip"
            :rows="wideResearchRows"
            @continue-normal="activateMode('normal')"
            @skip="handleWideResearchSkip" />

          <ChatMessage
            v-for="(message, index) in messages"
            :key="index"
            :message="message"
            :hideHeader="isConsecutiveAssistant(messages, index)"
            :modelTier="modelTier"
            @toolClick="handleToolClick" />

          <LoadingIndicator v-if="isLoading" :text="$t('Thinking')" />

          <div v-if="isTaskComplete" class="mt-4 rounded-[20px] border border-[var(--border-main)] bg-white px-4 py-4">
            <div class="flex items-center justify-between gap-4 flex-wrap">
              <span class="inline-flex items-center gap-2 rounded-full border border-[#bbf7d0] bg-[#f0fdf4] px-3 py-1 text-[13px] text-[#16a34a]">
                <CheckCircle2 :size="14" />
                Task completed
              </span>
              <div class="flex items-center gap-2 text-[13px] text-[var(--text-secondary)]">
                <span>How was this result?</span>
                <button v-for="star in 5" :key="star" class="text-lg transition-colors" :class="star <= rating ? 'text-[#f59e0b]' : 'text-black/20'" @click="saveRating(star)">★</button>
              </div>
            </div>

            <div class="mt-4">
              <div class="text-[13px] font-medium uppercase tracking-[0.08em] text-[var(--text-tertiary)]">Suggested follow-ups</div>
              <div class="mt-3 flex flex-wrap gap-2">
                <button v-for="suggestion in followups" :key="suggestion" class="followup-row" @click="applyFollowup(suggestion)">
                  <div class="flex items-center gap-3 min-w-0">
                    <span class="w-7 h-7 rounded-full bg-[var(--background-gray-main)] flex items-center justify-center text-[14px]">{{ followupIcon(suggestion) }}</span>
                    <span class="truncate text-sm text-[var(--text-primary)]">{{ suggestion }}</span>
                  </div>
                  <ArrowRight :size="15" class="text-[var(--icon-secondary)]" />
                </button>
              </div>
            </div>
          </div>
        </div>

        <div class="flex flex-col bg-[var(--background-gray-main)] sticky bottom-0">
          <button @click="handleFollow" v-if="!follow" class="flex items-center justify-center w-[36px] h-[36px] rounded-full bg-[var(--background-white-main)] hover:bg-[var(--background-gray-main)] clickable border border-[var(--border-main)] shadow-[0px_5px_16px_0px_var(--shadow-S),0px_0px_1.25px_0px_var(--shadow-S)] absolute -top-20 left-1/2 -translate-x-1/2">
            <ArrowDown class="text-[var(--icon-primary)]" :size="20" />
          </button>
          <PlanPanel v-if="plan && plan.steps.length > 0" :plan="plan" />
          <div class="pb-3">
            <InputModeToggleBar
              :activeMode="inputMode"
              :designModel="designModel"
              @select-mode="handleModeSelect"
              @apply-prompt="applyPrompt"
              @update:designModel="designModel = $event" />
            <ModeSuggestionPanel
              :mode="inputMode"
              :selectedSlidesTemplate="slidesTemplate"
              :selectedWebsiteCategory="websiteCategory"
              @apply-prompt="applyPrompt"
              @update:slidesTemplate="slidesTemplate = $event"
              @update:websiteCategory="websiteCategory = $event" />
          </div>
          <ChatBox
            ref="chatBoxRef"
            v-model="inputMessage"
            :rows="1"
            @submit="handleSubmit"
            :isRunning="isLoading"
            @stop="handleStop"
            :disabled="(currentUser?.credits ?? 0) <= 0"
            :attachments="attachments"
            :placeholder="placeholder" />
        </div>
      </div>
    </div>

    <ToolPanel ref="toolPanel" :size="toolPanelSize" :sessionId="sessionId" :realTime="realTime" :isShare="false" @jumpToRealTime="jumpToRealTime" />
  </SimpleBar>
</template>

<script setup lang="ts">
import SimpleBar from '../components/SimpleBar.vue';
import { ref, onMounted, watch, nextTick, onUnmounted, reactive, toRefs, computed } from 'vue';
import { useRouter, onBeforeRouteUpdate } from 'vue-router';
import { useI18n } from 'vue-i18n';
import ChatBox from '../components/ChatBox.vue';
import ChatMessage from '../components/ChatMessage.vue';
import ForgeModelDropdown from '../components/ForgeModelDropdown.vue';
import CreditsPopover from '../components/CreditsPopover.vue';
import InputModeToggleBar from '../components/InputModeToggleBar.vue';
import ModeSuggestionPanel from '../components/ModeSuggestionPanel.vue';
import WideResearchCard from '../components/WideResearchCard.vue';
import * as agentApi from '../api/agent';
import { Message, MessageContent, ToolContent, StepContent, AttachmentsContent, isConsecutiveAssistant } from '../types/message';
import {
  StepEventData,
  ToolEventData,
  MessageEventData,
  ErrorEventData,
  TitleEventData,
  PlanEventData,
  AgentSSEEvent,
  WideResearchSubjectsIdentifiedEventData,
  WideResearchSubjectCompleteEventData,
  WideResearchCompleteEventData,
} from '../types/event';
import ToolPanel from '../components/ToolPanel.vue';
import PlanPanel from '../components/PlanPanel.vue';
import { ArrowDown, PanelLeft, Share2, Download, MoreHorizontal, UsersRound, ArrowRight, CheckCircle2 } from 'lucide-vue-next';
import { showErrorToast, showInfoToast, showSuccessToast } from '../utils/toast';
import type { FileInfo } from '../api/file';
import { useLeftPanel } from '../composables/useLeftPanel';
import { useSessionFileList } from '../composables/useSessionFileList';
import { useFilePanel } from '../composables/useFilePanel';
import { useAuth } from '../composables/useAuth';
import { copyToClipboard } from '../utils/dom';
import { SessionStatus } from '../types/response';
import LoadingIndicator from '@/components/ui/LoadingIndicator.vue';
import { useInputMode, type InputMode } from '../composables/useInputMode';

const router = useRouter();
const { t } = useI18n();
const { toggleLeftPanel, isLeftPanelShow } = useLeftPanel();
const { showSessionFileList } = useSessionFileList();
const { hideFilePanel } = useFilePanel();
const { currentUser } = useAuth();
const {
  inputMode,
  designModel,
  slidesTemplate,
  websiteCategory,
  placeholder,
  activateMode,
  buildModeConfig,
} = useInputMode();

const createInitialState = () => ({
  inputMessage: '',
  isLoading: false,
  sessionId: undefined as string | undefined,
  messages: [] as Message[],
  toolPanelSize: 0,
  realTime: true,
  follow: true,
  title: 'New task',
  plan: undefined as PlanEventData | undefined,
  lastNoMessageTool: undefined as ToolContent | undefined,
  lastTool: undefined as ToolContent | undefined,
  lastEventId: undefined as string | undefined,
  cancelCurrentChat: null as (() => void) | null,
  attachments: [] as FileInfo[],
  goal: '',
  maxBudget: 0,
  spentCredits: 0,
  runMode: 'auto',
  permissions: 'standard',
  riskLevel: 'low',
  modelTier: 'regular',
  wideResearch: false,
  isTaskComplete: false,
  followups: [] as string[],
});

const state = reactive(createInitialState());
const {
  inputMessage,
  isLoading,
  sessionId,
  messages,
  toolPanelSize,
  realTime,
  follow,
  title,
  plan,
  lastNoMessageTool,
  lastTool,
  lastEventId,
  cancelCurrentChat,
  attachments,
  goal,
  maxBudget,
  spentCredits,
  runMode,
  permissions,
  riskLevel,
  modelTier,
  wideResearch,
  isTaskComplete,
  followups,
} = toRefs(state);

const toolPanel = ref<InstanceType<typeof ToolPanel>>();
const chatBoxRef = ref<InstanceType<typeof ChatBox>>();
const simpleBarRef = ref<InstanceType<typeof SimpleBar>>();
const observerRef = ref<HTMLDivElement>();
const chatContainerRef = ref<HTMLDivElement>();
const rating = ref(0);
const showOverflow = ref(false);
const nowTick = ref(Date.now());
let nowTickTimer: number | null = null;
const wideResearchSubjects = ref<Array<{ name: string; status: 'waiting' | 'running' | 'completed' | 'skipped' }>>([]);
const wideResearchRows = ref<Array<Record<string, any>>>([]);
const wideResearchCompleted = ref(0);
const wideResearchStarted = ref(false);
const wideResearchStartedAt = ref<number | null>(null);
const ratingKey = computed(() => sessionId.value ? `forge-rating-${sessionId.value}` : '');
const showWideResearchSkip = computed(() => !!wideResearchStartedAt.value && nowTick.value - wideResearchStartedAt.value > 60_000);

const runModeLabel = computed(() => runMode.value === 'checkpoint' ? 'Checkpoint' : 'Auto Mode');
const permissionsLabel = computed(() => permissions.value === 'guarded' ? 'Guarded Access' : 'Standard Access');
const riskLabel = computed(() => `${String(riskLevel.value || 'low').charAt(0).toUpperCase()}${String(riskLevel.value || 'low').slice(1)} Risk`);

const cleanErrorMessage = (raw: string): string => {
  const source = String(raw || '').trim();
  if (!source) return 'Forge hit a blocker on this run. Retry the task or adjust the prompt.';
  if (source.toLowerCase().includes('404')) return 'Forge hit a dead page while browsing. Try again and it will move to a different source.';
  if (source.toLowerCase().includes('unexpected tokens remaining')) return 'Forge received a malformed tool response during browsing. Retry the run and it should recover cleanly.';
  return source.length > 220 ? `${source.slice(0, 217)}...` : source;
};

const resetState = () => {
  if (cancelCurrentChat.value) {
    cancelCurrentChat.value();
  }
  Object.assign(state, createInitialState());
  activateMode('normal');
  designModel.value = 'Forge Image v1';
  slidesTemplate.value = 'Minimal';
  websiteCategory.value = 'SaaS';
  wideResearchSubjects.value = [];
  wideResearchRows.value = [];
  wideResearchCompleted.value = 0;
  wideResearchStarted.value = false;
  wideResearchStartedAt.value = null;
  rating.value = 0;
  showOverflow.value = false;
};

watch(messages, async () => {
  await nextTick();
  if (follow.value) {
    simpleBarRef.value?.scrollToBottom();
  }
}, { deep: true });

const getLastStep = (): StepContent | undefined => {
  return messages.value.filter(message => message.type === 'step').pop()?.content as StepContent;
};

const buildFallbackFollowups = () => {
  const base = goal.value || title.value || 'this task';
  return [
    `Summarize the key findings from ${base}`,
    `Turn ${base} into a spreadsheet`,
    `Give me the next best actions for ${base}`,
  ];
};

const saveRating = (value: number) => {
  rating.value = value;
  if (ratingKey.value) {
    localStorage.setItem(ratingKey.value, String(value));
  }
  showSuccessToast('Thanks for the feedback');
};

const loadFollowups = async () => {
  if (!sessionId.value) return;
  try {
    followups.value = await agentApi.getSessionFollowups(sessionId.value);
  } catch {
    followups.value = buildFallbackFollowups();
  }
};

const markTaskComplete = async () => {
  isTaskComplete.value = true;
  await loadFollowups();
  if (ratingKey.value) {
    const saved = Number(localStorage.getItem(ratingKey.value) || 0);
    rating.value = Number.isFinite(saved) ? saved : 0;
  }
};

const handleMessageEvent = (messageData: MessageEventData) => {
  messages.value.push({
    type: messageData.role,
    content: { ...messageData } as MessageContent,
  });

  if (messageData.attachments?.length > 0) {
    messages.value.push({
      type: 'attachments',
      content: { ...messageData } as AttachmentsContent,
    });
  }
};

const handleToolEvent = (toolData: ToolEventData) => {
  const lastStep = getLastStep();
  const toolContent: ToolContent = { ...toolData };
  if (lastTool.value && lastTool.value.tool_call_id === toolContent.tool_call_id) {
    Object.assign(lastTool.value, toolContent);
  } else {
    if (lastStep?.status === 'running') {
      lastStep.tools.push(toolContent);
    } else {
      messages.value.push({ type: 'tool', content: toolContent });
    }
    lastTool.value = toolContent;
  }
  if (toolContent.name !== 'message') {
    lastNoMessageTool.value = toolContent;
    if (realTime.value) {
      toolPanel.value?.showToolPanel(toolContent, true);
    }
  }
};

const handleStepEvent = (stepData: StepEventData) => {
  const lastStep = getLastStep();
  if (stepData.status === 'running') {
    messages.value.push({
      type: 'step',
      content: { ...stepData, tools: [] } as StepContent,
    });
    isTaskComplete.value = false;
  } else if (stepData.status === 'completed') {
    if (lastStep) lastStep.status = stepData.status;
  } else if (stepData.status === 'failed') {
    isLoading.value = false;
    plan.value = undefined;
  }
};

const handleErrorEvent = (errorData: ErrorEventData) => {
  isLoading.value = false;
  const cleanedError = cleanErrorMessage(errorData.error || '');
  messages.value.push({
    type: 'assistant',
    content: {
      content: `Run blocked: ${cleanedError}`,
      timestamp: errorData.timestamp,
    } as MessageContent,
  });
};

const handleTitleEvent = (titleData: TitleEventData) => {
  title.value = titleData.title;
};

const handlePlanEvent = (planData: PlanEventData) => {
  plan.value = planData;
};

const handleWideResearchSubjects = (data: WideResearchSubjectsIdentifiedEventData) => {
  activateMode('wide_research');
  wideResearchSubjects.value = data.subjects.map((subject, index) => ({
    name: subject,
    status: 'running',
  }));
  wideResearchRows.value = [];
  wideResearchCompleted.value = 0;
  wideResearchStarted.value = true;
  wideResearchStartedAt.value = Date.now();
};

const handleWideResearchSubjectComplete = (data: WideResearchSubjectCompleteEventData) => {
  if (!wideResearchSubjects.value.length) return;
  wideResearchStarted.value = true;
  wideResearchCompleted.value = data.completed;
  wideResearchRows.value = [
    ...wideResearchRows.value.filter((row) => row.name !== data.subject?.name),
    data.subject,
  ];
  wideResearchSubjects.value = wideResearchSubjects.value.map((subject, index) => {
    if (index === data.index) return { ...subject, name: data.subject?.name || subject.name, status: 'completed' };
    return subject;
  });
};

const handleWideResearchComplete = (data: WideResearchCompleteEventData) => {
  wideResearchStarted.value = false;
  wideResearchCompleted.value = data.subjects?.length || wideResearchCompleted.value;
  if (Array.isArray(data.subjects) && data.subjects.length > 0) {
    wideResearchRows.value = data.subjects;
    wideResearchSubjects.value = data.subjects.map((subject) => ({
      name: String(subject.name || 'Subject'),
      status: 'completed',
    }));
  }
};

const applyPrompt = (prompt: string) => {
  inputMessage.value = prompt;
  chatBoxRef.value?.focusInput();
};

const handleModeSelect = (mode: InputMode) => {
  activateMode(mode);
  chatBoxRef.value?.focusInput();
};

const handleWideResearchSkip = () => {
  wideResearchSubjects.value = wideResearchSubjects.value.map((subject) =>
    subject.status === 'waiting' || subject.status === 'running'
      ? { ...subject, status: 'skipped' }
      : subject
  );
  showInfoToast('Forge will finish with the subjects it already has.');
};

const handleEvent = async (event: AgentSSEEvent) => {
  try {
    if (event.event === 'message') {
      handleMessageEvent(event.data as MessageEventData);
    } else if (event.event === 'tool') {
      handleToolEvent(event.data as ToolEventData);
    } else if (event.event === 'step') {
      handleStepEvent(event.data as StepEventData);
    } else if (event.event === 'done') {
      isLoading.value = false;
      await markTaskComplete();
    } else if (event.event === 'error') {
      handleErrorEvent(event.data as ErrorEventData);
    } else if (event.event === 'title') {
      handleTitleEvent(event.data as TitleEventData);
    } else if (event.event === 'plan') {
      handlePlanEvent(event.data as PlanEventData);
    } else if (event.event === 'wide_research_subjects_identified') {
      handleWideResearchSubjects(event.data as WideResearchSubjectsIdentifiedEventData);
    } else if (event.event === 'wide_research_subject_complete') {
      handleWideResearchSubjectComplete(event.data as WideResearchSubjectCompleteEventData);
    } else if (event.event === 'wide_research_complete') {
      handleWideResearchComplete(event.data as WideResearchCompleteEventData);
    }
    lastEventId.value = event.data.event_id;
  } catch (e) {
    console.error('Event parse error:', e);
  }
};

const handleSubmit = () => {
  chat(inputMessage.value, attachments.value);
};

const chat = async (message: string = '', files: FileInfo[] = []) => {
  if (!sessionId.value) return;

  if (cancelCurrentChat.value) {
    cancelCurrentChat.value();
    cancelCurrentChat.value = null;
  }

  if (message.trim()) {
    messages.value.push({
      type: 'user',
      content: { content: message, timestamp: Math.floor(Date.now() / 1000) } as MessageContent,
    });
  }

  if (files.length > 0) {
    messages.value.push({
      type: 'attachments',
      content: { role: 'user', attachments: files } as AttachmentsContent,
    });
  }

  follow.value = true;
  inputMessage.value = '';
  attachments.value = [];
  isLoading.value = true;
  isTaskComplete.value = false;

  try {
    cancelCurrentChat.value = await agentApi.chatWithSession(
      sessionId.value,
      message,
      lastEventId.value,
      files.map((file: FileInfo) => ({ file_id: file.file_id, filename: file.filename })),
      inputMode.value,
      buildModeConfig(),
      {
        onOpen: () => {
          isLoading.value = true;
        },
        onMessage: ({ event, data }) => {
          void handleEvent({
            event: event as AgentSSEEvent['event'],
            data: data as AgentSSEEvent['data'],
          });
        },
        onClose: () => {
          isLoading.value = false;
          cancelCurrentChat.value = null;
        },
        onError: () => {
          isLoading.value = false;
          cancelCurrentChat.value = null;
        },
      }
    );
  } catch (error) {
    console.error('Chat error:', error);
    isLoading.value = false;
    cancelCurrentChat.value = null;
  }
};

const restoreSession = async () => {
  if (!sessionId.value) {
    showErrorToast(t('Session not found'));
    return;
  }
  const session = await agentApi.getSession(sessionId.value);
  goal.value = session.goal || '';
  maxBudget.value = session.max_budget || 0;
  spentCredits.value = session.spent_credits || session.estimated_cost || 0;
  runMode.value = session.mode || 'auto';
  permissions.value = session.permissions || 'standard';
  riskLevel.value = session.risk_level || 'low';
  modelTier.value = session.model_tier || 'regular';
  wideResearch.value = !!session.wide_research;
  activateMode((session.input_mode as any) || (session.wide_research ? 'wide_research' : 'normal'));
  designModel.value = (session.mode_config?.designModel as any) || 'Forge Image v1';
  slidesTemplate.value = session.mode_config?.slidesTemplate || 'Minimal';
  websiteCategory.value = session.mode_config?.websiteCategory || 'SaaS';
  realTime.value = false;
  for (const event of session.events) {
    await handleEvent(event);
  }
  realTime.value = true;
  if (session.status === SessionStatus.RUNNING || session.status === SessionStatus.PENDING) {
    await chat();
  } else if (session.status === SessionStatus.COMPLETED) {
    await markTaskComplete();
  }
  agentApi.clearUnreadMessageCount(sessionId.value);
};

onBeforeRouteUpdate((to, _, next) => {
  toolPanel.value?.hideToolPanel();
  hideFilePanel();
  resetState();
  if (to.params.sessionId) {
    messages.value = [];
    sessionId.value = String(to.params.sessionId);
    void restoreSession();
  }
  next();
});

onMounted(() => {
  hideFilePanel();
  nowTickTimer = window.setInterval(() => {
    nowTick.value = Date.now();
  }, 1000);
  const routeParams = router.currentRoute.value.params;
  if (routeParams.sessionId) {
    sessionId.value = String(routeParams.sessionId);
    const message = history.state?.message;
    const files: FileInfo[] = history.state?.files;
    const routeInputMode = history.state?.inputMode;
    const routeModeConfig = history.state?.modeConfig;
    if (routeInputMode) {
      activateMode(routeInputMode);
    }
    if (routeModeConfig?.designModel) {
      designModel.value = routeModeConfig.designModel;
    }
    if (routeModeConfig?.slidesTemplate) {
      slidesTemplate.value = routeModeConfig.slidesTemplate;
    }
    if (routeModeConfig?.websiteCategory) {
      websiteCategory.value = routeModeConfig.websiteCategory;
    }
    history.replaceState({}, document.title);
    if (message) {
      void chat(message, files);
    } else {
      void restoreSession();
    }
  }
});

onUnmounted(() => {
  if (nowTickTimer) {
    window.clearInterval(nowTickTimer);
    nowTickTimer = null;
  }
  try {
    if (cancelCurrentChat.value) {
      cancelCurrentChat.value();
      cancelCurrentChat.value = null;
    }
  } catch (error) {
    console.error('Error cancelling chat on unmount:', error);
  }
});

const isLastNoMessageTool = (tool: ToolContent) => tool.tool_call_id === lastNoMessageTool.value?.tool_call_id;

const isLiveTool = (tool: ToolContent) => {
  if (tool.status === 'calling') return true;
  if (!isLastNoMessageTool(tool)) return false;
  if (tool.timestamp && tool.timestamp > Date.now() - 5 * 60 * 1000) return true;
  return false;
};

const handleToolClick = (tool: ToolContent) => {
  realTime.value = false;
  if (sessionId.value) {
    toolPanel.value?.showToolPanel(tool, isLiveTool(tool));
  }
};

const jumpToRealTime = () => {
  realTime.value = true;
  if (lastNoMessageTool.value) {
    toolPanel.value?.showToolPanel(lastNoMessageTool.value, isLiveTool(lastNoMessageTool.value));
  }
};

const handleFollow = () => {
  follow.value = true;
  simpleBarRef.value?.scrollToBottom();
};

const handleScroll = () => {
  follow.value = simpleBarRef.value?.isScrolledToBottom() ?? false;
};

const handleStop = () => {
  if (sessionId.value) {
    agentApi.stopSession(sessionId.value);
  }
};

const handleCopyLink = async () => {
  if (!sessionId.value) return;
  const shareUrl = `${window.location.origin}/share/${sessionId.value}`;
  const success = await copyToClipboard(shareUrl);
  if (success) {
    showSuccessToast('Copied!');
  } else {
    showErrorToast('Failed to copy link');
  }
  showOverflow.value = false;
};

const handleExport = () => {
  const body = messages.value.map((message) => {
    if ('content' in message.content && typeof (message.content as any).content === 'string') {
      return `## ${message.type}\n\n${(message.content as any).content}`;
    }
    return `## ${message.type}\n\n${JSON.stringify(message.content, null, 2)}`;
  }).join('\n\n');
  const blob = new Blob([`# ${title.value}\n\n${body}`], { type: 'text/markdown;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = `${(title.value || 'forge-task').replace(/[^a-z0-9]+/gi, '-').toLowerCase()}.md`;
  anchor.click();
  URL.revokeObjectURL(url);
};

const renameCurrentTask = async () => {
  if (!sessionId.value) return;
  const nextTitle = window.prompt('Rename task', title.value || '');
  if (!nextTitle?.trim()) return;
  await agentApi.renameSession(sessionId.value, nextTitle.trim());
  title.value = nextTitle.trim();
  showOverflow.value = false;
};

const deleteCurrentTask = async () => {
  if (!sessionId.value || !window.confirm('Delete this task?')) return;
  await agentApi.deleteSession(sessionId.value);
  showOverflow.value = false;
  router.push('/');
};

const applyFollowup = (suggestion: string) => {
  inputMessage.value = suggestion;
  void handleSubmit();
};

const followupIcon = (suggestion: string) => {
  const lower = suggestion.toLowerCase();
  if (lower.includes('spreadsheet')) return '📊';
  if (lower.includes('slides')) return '📁';
  if (lower.includes('summarize')) return '💬';
  return '🔧';
};
</script>

<style scoped>
.header-action-btn,
.icon-header-btn,
.run-pill,
.followup-row,
.overflow-action {
  transition: background-color 0.15s ease;
}

.header-action-btn {
  height: 36px;
  padding: 0 14px;
  border-radius: 9999px;
  border: 1px solid var(--border-btn-main);
  background: var(--background-white-main);
  color: var(--text-secondary);
  font-size: 13px;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.icon-header-btn {
  width: 36px;
  height: 36px;
  border-radius: 9999px;
  border: 1px solid var(--border-btn-main);
  background: var(--background-white-main);
  color: var(--text-secondary);
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.header-action-btn:hover,
.icon-header-btn:hover,
.followup-row:hover,
.overflow-action:hover {
  background: var(--fill-tsp-white-light);
}

.run-pill {
  display: inline-flex;
  align-items: center;
  height: 32px;
  padding: 0 12px;
  border-radius: 9999px;
  border: 1px solid var(--border-btn-main);
  background: var(--background-white-main);
  color: var(--text-secondary);
  font-size: 12px;
}

.followup-row {
  width: auto;
  max-width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  border-radius: 9999px;
  border: 1px solid var(--border-main);
  background: var(--background-white-main);
  padding: 8px 14px;
  min-height: 42px;
}

.overflow-action {
  width: 100%;
  height: 36px;
  border-radius: 10px;
  padding: 0 12px;
  text-align: left;
  font-size: 13px;
  color: var(--text-primary);
}
</style>
