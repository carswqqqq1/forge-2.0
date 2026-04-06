<template>
  <Teleport to="body">
    <div v-if="isSearchModalOpen" class="fixed inset-0 z-[80] flex items-start justify-center bg-black/20 backdrop-blur-sm px-4 pt-20" @click.self="closeSearchModal">
      <div class="w-full max-w-[620px] rounded-[28px] border border-black/5 bg-white shadow-[0px_30px_80px_0px_rgba(0,0,0,0.18)] overflow-hidden">
        <div class="px-5 pt-5 pb-3 border-b border-[var(--border-main)]">
          <div class="flex items-center gap-3 h-12 rounded-[16px] border border-[var(--border-main)] bg-[var(--background-gray-main)] px-4">
            <Search :size="18" class="text-[var(--icon-secondary)]" />
            <input
              ref="inputRef"
              v-model="query"
              type="text"
              placeholder="Search tasks..."
              class="w-full bg-transparent text-[15px] outline-none text-[var(--text-primary)] placeholder:text-[var(--text-disable)]" />
          </div>
          <button class="mt-3 inline-flex items-center gap-2 rounded-[14px] bg-[var(--Button-primary-black)] text-[var(--text-onblack)] px-4 py-2 text-sm font-medium" @click="createTask">
            <Plus :size="16" />
            New task
          </button>
        </div>
        <div class="max-h-[70vh] overflow-y-auto px-3 py-3">
          <div v-for="group in groupedResults" :key="group.label" class="mb-5 last:mb-0">
            <div class="px-2 pb-2 text-[12px] font-medium uppercase tracking-[0.08em] text-[var(--text-tertiary)]">{{ group.label }}</div>
            <button
              v-for="session in group.items"
              :key="session.session_id"
              class="w-full flex items-start gap-3 rounded-[16px] px-3 py-3 text-left hover:bg-[var(--fill-tsp-white-light)]"
              @click="openSession(session.session_id)">
              <div class="mt-0.5">
                <component :is="getSessionIcon(session)" :size="16" class="text-[var(--icon-secondary)]" />
              </div>
              <div class="min-w-0 flex-1">
                <div class="flex items-start justify-between gap-3">
                  <div class="truncate text-[14px] font-semibold text-[var(--text-primary)]">
                    {{ session.title || 'Untitled task' }}
                  </div>
                  <div class="shrink-0 text-[12px] text-[var(--text-tertiary)]">{{ formatStamp(session.latest_message_at) }}</div>
                </div>
                <div class="mt-1 truncate text-[13px] text-[var(--text-secondary)]">
                  {{ session.latest_message || 'Open this task to continue where you left off.' }}
                </div>
              </div>
            </button>
          </div>
          <div v-if="groupedResults.length === 0" class="px-4 py-10 text-center text-sm text-[var(--text-tertiary)]">
            No tasks match this search yet.
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue';
import { useRouter } from 'vue-router';
import { Search, Plus, Globe, SearchCheck, Code2, FileText } from 'lucide-vue-next';
import { useSearchModal } from '../composables/useSearchModal';
import { getSessions } from '../api/agent';
import type { ListSessionItem } from '../types/response';

const router = useRouter();
const { isSearchModalOpen, closeSearchModal, openSearchModal } = useSearchModal();
const inputRef = ref<HTMLInputElement | null>(null);
const query = ref('');
const sessions = ref<ListSessionItem[]>([]);

const loadSessions = async () => {
  try {
    const response = await getSessions();
    sessions.value = response.sessions;
  } catch (error) {
    console.error('Failed to load search sessions:', error);
  }
};

const filtered = computed(() => {
  const value = query.value.trim().toLowerCase();
  if (!value) return sessions.value;
  return sessions.value.filter((session) =>
    `${session.title || ''} ${session.latest_message || ''}`.toLowerCase().includes(value)
  );
});

const bucketLabel = (timestamp: number | null) => {
  if (!timestamp) return 'Last 30 days';
  const now = new Date();
  const date = new Date(timestamp * 1000);
  const diff = now.getTime() - date.getTime();
  const days = diff / (1000 * 60 * 60 * 24);
  if (days < 1 && now.getDate() === date.getDate()) return 'Today';
  if (days < 2) return 'Yesterday';
  if (days <= 7) return 'Last 7 days';
  return 'Last 30 days';
};

const groupedResults = computed(() => {
  const order = ['Today', 'Yesterday', 'Last 7 days', 'Last 30 days'];
  return order
    .map((label) => ({
      label,
      items: filtered.value.filter((session) => bucketLabel(session.latest_message_at) === label),
    }))
    .filter((group) => group.items.length > 0);
});

const getSessionIcon = (session: ListSessionItem) => {
  const text = `${session.title || ''} ${session.latest_message || ''}`.toLowerCase();
  if (text.includes('research') || text.includes('search')) return SearchCheck;
  if (text.includes('website') || text.includes('browser')) return Globe;
  if (text.includes('code') || text.includes('build')) return Code2;
  return FileText;
};

const formatStamp = (timestamp: number | null) => {
  if (!timestamp) return '';
  const date = new Date(timestamp * 1000);
  const now = new Date();
  const sameDay = now.toDateString() === date.toDateString();
  if (sameDay) {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  }
  return date.toLocaleDateString([], { weekday: 'long' });
};

const createTask = () => {
  closeSearchModal();
  router.push('/');
};

const openSession = (sessionId: string) => {
  closeSearchModal();
  router.push(`/chat/${sessionId}`);
};

watch(isSearchModalOpen, async (open) => {
  if (open) {
    await loadSessions();
    await nextTick();
    inputRef.value?.focus();
  } else {
    query.value = '';
  }
});

const handleKeydown = (event: KeyboardEvent) => {
  if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === 'k') {
    event.preventDefault();
    openSearchModal();
  }
  if (event.key === 'Escape' && isSearchModalOpen.value) {
    closeSearchModal();
  }
};

onMounted(() => {
  window.addEventListener('keydown', handleKeydown);
});

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown);
});
</script>
