<template>
  <div
    @click="handleSessionClick"
    class="group flex items-center rounded-[10px] cursor-pointer transition-colors w-full gap-[10px] h-[40px] flex-shrink-0 pointer-events-auto ps-[9px] pe-[6px] active:bg-[var(--fill-tsp-white-dark)]"
    :class="isCurrentSession ? 'bg-[var(--fill-tsp-white-main)]' : 'hover:bg-[var(--fill-tsp-white-light)]'">
    <div class="shrink-0 size-[18px] flex items-center justify-center relative">
      <component :is="taskIconComponent" :size="18" class="text-[var(--icon-primary)]" />
    </div>

    <div class="shrink-0 size-[14px] flex items-center justify-center">
      <LoaderCircle v-if="statusType === 'running'" :size="14" class="animate-spin text-[#2b6cf6]" />
      <div v-else-if="statusType === 'done'" class="status-badge status-done">
        <Check :size="9" class="text-white" />
      </div>
      <div v-else-if="statusType === 'failed'" class="status-badge status-failed">
        <X :size="9" class="text-white" />
      </div>
      <Circle v-else :size="12" class="text-[#9ca3af]" />
    </div>

    <div class="flex-1 min-w-0 flex gap-[6px] items-center text-[14px] text-[var(--text-primary)]">
      <span class="truncate" :title="session.title || 'New task'">
        {{ session.title || 'New task' }}
      </span>
    </div>

    <div class="shrink-0 flex items-center gap-1">
      <div
        @click.stop="handleSessionMenuClick"
        class="group-hover:flex hidden size-8 rounded-[8px] cursor-pointer items-center justify-center hover:bg-[var(--fill-tsp-white-light)]"
        :class="isContextMenuOpen ? '!flex bg-[var(--fill-tsp-white-light)]' : ''"
        aria-expanded="false" aria-haspopup="dialog">
        <Ellipsis :size="18" class="text-[var(--icon-tertiary)]" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import {
  Ellipsis,
  Code2,
  Search,
  FileText,
  Globe,
  LoaderCircle,
  Circle,
  Check,
  X,
  PencilLine,
  Share2,
  Trash,
} from 'lucide-vue-next';
import { computed, ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { useRoute, useRouter } from 'vue-router';
import { ListSessionItem, SessionStatus } from '../types/response';
import { useContextMenu, createDangerMenuItem, createMenuItem } from '../composables/useContextMenu';
import { useDialog } from '../composables/useDialog';
import { deleteSession, renameSession, shareSession } from '../api/agent';
import { showSuccessToast, showErrorToast } from '../utils/toast';
import { copyToClipboard } from '../utils/dom';

interface Props {
  session: ListSessionItem;
}

const props = defineProps<Props>();

const { t } = useI18n();
const route = useRoute();
const router = useRouter();
const { showContextMenu } = useContextMenu();
const { showConfirmDialog } = useDialog();
const isContextMenuOpen = ref(false);

const emit = defineEmits<{
  (e: 'deleted', sessionId: string): void
}>();

const currentSessionId = computed(() => route.params.sessionId as string);
const isCurrentSession = computed(() => currentSessionId.value === props.session.session_id);

const taskIconComponent = computed(() => {
  const title = (props.session.title || '').toLowerCase();
  if (title.includes('code') || title.includes('script') || title.includes('python') || title.includes('javascript') || title.includes('debug')) {
    return Code2;
  }
  if (title.includes('search') || title.includes('find') || title.includes('research') || title.includes('compare')) {
    return Search;
  }
  if (title.includes('web') || title.includes('website') || title.includes('browse') || title.includes('page')) {
    return Globe;
  }
  return FileText;
});

const statusType = computed<'running' | 'done' | 'failed' | 'pending'>(() => {
  const latest = `${props.session.latest_message || ''}`.toLowerCase();
  if (props.session.status === SessionStatus.RUNNING) return 'running';
  if (props.session.status === SessionStatus.COMPLETED && (latest.includes('run blocked') || latest.includes('task encountered an error') || latest.includes('something went wrong'))) {
    return 'failed';
  }
  if (props.session.status === SessionStatus.COMPLETED) return 'done';
  return 'pending';
});

const handleSessionClick = () => {
  router.push(`/chat/${props.session.session_id}`);
};

const handleRename = async () => {
  const nextTitle = window.prompt('Rename task', props.session.title || '');
  if (!nextTitle || !nextTitle.trim()) return;
  try {
    await renameSession(props.session.session_id, nextTitle.trim());
    showSuccessToast('Task renamed');
  } catch {
    showErrorToast('Failed to rename task');
  }
};

const handleShare = async () => {
  try {
    await shareSession(props.session.session_id);
    const copied = await copyToClipboard(`${window.location.origin}/share/${props.session.session_id}`);
    if (copied) {
      showSuccessToast('Share link copied');
    } else {
      showSuccessToast('Task shared');
    }
  } catch {
    showErrorToast('Failed to share task');
  }
};

const handleSessionMenuClick = (event: MouseEvent) => {
  event.stopPropagation();
  const target = event.currentTarget as HTMLElement;
  isContextMenuOpen.value = true;

  showContextMenu(
    props.session.session_id,
    target,
    [
      createMenuItem('rename', 'Rename', { icon: PencilLine }),
      createMenuItem('share', 'Share', { icon: Share2 }),
      createDangerMenuItem('delete', t('Delete'), { icon: Trash }),
    ],
    (itemKey: string) => {
      if (itemKey === 'rename') {
        void handleRename();
      } else if (itemKey === 'share') {
        void handleShare();
      } else if (itemKey === 'delete') {
        showConfirmDialog({
          title: t('Are you sure you want to delete this session?'),
          content: t('The chat history of this session cannot be recovered after deletion.'),
          confirmText: t('Delete'),
          cancelText: t('Cancel'),
          confirmType: 'danger',
          onConfirm: () => {
            deleteSession(props.session.session_id).then(() => {
              showSuccessToast(t('Deleted successfully'));
              emit('deleted', props.session.session_id);
            }).catch(() => {
              showErrorToast(t('Failed to delete session'));
            });
            if (isCurrentSession.value) {
              router.push('/');
            }
          }
        });
      }
    },
    () => {
      isContextMenuOpen.value = false;
    }
  );
};
</script>

<style scoped>
.status-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 14px;
  height: 14px;
  border-radius: 9999px;
}

.status-done {
  background: #22c55e;
}

.status-failed {
  background: #ef4444;
}
</style>
