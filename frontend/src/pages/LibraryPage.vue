<template>
  <div class="flex-1 min-w-0 h-full overflow-y-auto bg-[var(--background-gray-main)]">
    <div class="max-w-[1180px] mx-auto px-8 py-8">
      <div class="flex items-center justify-between gap-4 flex-wrap">
        <h1 class="text-[32px] font-semibold tracking-[-0.03em] text-[var(--text-primary)]">Library</h1>
        <div class="flex items-center gap-2 flex-wrap">
          <button class="rounded-full border border-[var(--border-main)] bg-white px-4 py-2 text-sm font-medium">All ▾</button>
          <button class="rounded-full border border-[var(--border-main)] bg-white px-4 py-2 text-sm font-medium">⭐ My favorites</button>
        </div>
        <div class="flex items-center gap-2 flex-wrap ml-auto">
          <input v-model="query" type="text" placeholder="Search files..." class="h-10 rounded-full border border-[var(--border-main)] bg-white px-4 text-sm outline-none" />
          <button class="view-btn" :class="{ 'view-btn-active': viewMode === 'grid' }" @click="viewMode = 'grid'"><LayoutGrid :size="16" /></button>
          <button class="view-btn" :class="{ 'view-btn-active': viewMode === 'list' }" @click="viewMode = 'list'"><List :size="16" /></button>
        </div>
      </div>

      <div class="mt-8 space-y-8">
        <section v-for="group in filteredGroups" :key="group.sessionId">
          <div class="flex items-end justify-between gap-4 mb-4">
            <div class="text-[18px] font-semibold text-[var(--text-primary)]">{{ group.title }}</div>
            <div class="text-[13px] text-[var(--text-tertiary)]">{{ group.date }}</div>
          </div>
          <div :class="viewMode === 'grid' ? 'grid md:grid-cols-2 xl:grid-cols-3 gap-4' : 'flex flex-col gap-3'">
            <article v-for="file in group.files" :key="file.file_id" class="rounded-[22px] border border-[var(--border-main)] bg-white p-4 shadow-[0px_10px_24px_0px_rgba(0,0,0,0.03)]">
              <div class="flex items-start justify-between gap-3">
                <div class="flex items-center gap-3 min-w-0">
                  <div class="w-10 h-10 rounded-[14px] bg-[var(--background-gray-main)] flex items-center justify-center">
                    <component :is="getFileType(file.filename).icon" />
                  </div>
                  <div class="min-w-0">
                    <div class="truncate text-sm font-medium text-[var(--text-primary)]">{{ file.filename }}</div>
                    <div class="text-xs text-[var(--text-tertiary)]">{{ file.content_type || 'Document' }}</div>
                  </div>
                </div>
                <button class="h-8 w-8 rounded-full hover:bg-[var(--fill-tsp-white-light)] flex items-center justify-center">
                  <MoreHorizontal :size="16" class="text-[var(--icon-secondary)]" />
                </button>
              </div>
              <div class="mt-4 rounded-[16px] bg-[var(--background-gray-main)] px-3 py-3 text-[12px] leading-6 text-[var(--text-secondary)] min-h-[88px]">
                {{ previewFor(file) }}
              </div>
            </article>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { LayoutGrid, List, MoreHorizontal } from 'lucide-vue-next';
import { getSessions, getSessionFiles } from '../api/agent';
import type { FileInfo } from '../api/file';
import { getFileType } from '../utils/fileType';

interface LibraryGroup {
  sessionId: string;
  title: string;
  date: string;
  latestMessage: string;
  files: FileInfo[];
}

const groups = ref<LibraryGroup[]>([]);
const query = ref('');
const viewMode = ref<'grid' | 'list'>('grid');

const loadLibrary = async () => {
  const sessionResponse = await getSessions();
  const enriched = await Promise.all(
    sessionResponse.sessions.map(async (session) => {
      const files = await getSessionFiles(session.session_id).catch(() => []);
      return {
        sessionId: session.session_id,
        title: session.title || 'Untitled task',
        date: session.latest_message_at ? new Date(session.latest_message_at * 1000).toLocaleDateString() : '',
        latestMessage: session.latest_message || '',
        files,
      };
    })
  );
  groups.value = enriched.filter((group) => group.files.length > 0);
};

const filteredGroups = computed(() => {
  const value = query.value.trim().toLowerCase();
  if (!value) return groups.value;
  return groups.value
    .map((group) => ({
      ...group,
      files: group.files.filter((file) => `${file.filename} ${group.title}`.toLowerCase().includes(value)),
    }))
    .filter((group) => group.files.length > 0);
});

const previewFor = (file: FileInfo) => {
  const type = file.filename.split('.').pop()?.toUpperCase() || 'FILE';
  return `${type} file from this Forge task. Open it from the task thread to inspect the full output, preview, or download the latest version.`;
};

onMounted(() => {
  loadLibrary().catch((error) => {
    console.error('Failed to load library:', error);
  });
});
</script>

<style scoped>
.view-btn {
  width: 40px;
  height: 40px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 9999px;
  border: 1px solid var(--border-main);
  background: white;
  color: var(--text-secondary);
}

.view-btn-active {
  color: var(--text-primary);
  background: var(--background-gray-main);
}
</style>
