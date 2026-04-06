<template>
  <div :class="isLeftPanelShow ? 'h-full flex flex-col' : 'h-full flex flex-col fixed top-0 start-0 bottom-0 z-[1]'" :style="panelStyle">
    <div
      :class="isLeftPanelShow
        ? 'flex flex-col overflow-hidden bg-[var(--background-nav)] h-full opacity-100 translate-x-0'
        : 'flex flex-col overflow-hidden bg-[var(--background-nav)] fixed top-1 start-1 bottom-1 z-[1] border-1 border-[var(--border-main)] rounded-xl shadow-[0px_8px_32px_0px_rgba(0,0,0,0.16),0px_0px_0px_1px_rgba(0,0,0,0.06)] opacity-0 pointer-events-none -translate-x-10'"
      :style="innerPanelStyle">
      <div class="flex items-center justify-between px-3 h-[52px] flex-shrink-0">
        <button class="flex h-7 w-7 items-center justify-center cursor-pointer hover:bg-[var(--fill-tsp-gray-main)] rounded-md" @click="toggleLeftPanel">
          <PanelLeft class="h-5 w-5 text-[var(--icon-secondary)]" />
        </button>
        <button
          class="flex h-8 w-8 items-center justify-center cursor-pointer hover:bg-[var(--fill-tsp-gray-main)] rounded-md"
          @click="showInfoToast('No notifications yet')">
          <Bell :size="16" class="text-[var(--icon-secondary)]" />
        </button>
      </div>

      <div class="flex flex-col flex-1 min-h-0 px-[8px] pb-0">
        <button
          @click="handleNewTaskClick"
          class="flex items-center rounded-[14px] cursor-pointer transition-colors w-full gap-[12px] h-[44px] ps-[12px] pe-[12px] mb-1 bg-[var(--fill-tsp-white-main)] hover:bg-[var(--fill-tsp-white-light)]">
          <SquarePen :size="18" class="text-[var(--text-primary)] shrink-0" />
          <span class="truncate text-[14px] text-[var(--text-primary)] font-medium">New Task</span>
        </button>

        <button class="sidebar-nav-item" @click="showInfoToast('Agents workspace coming soon')">
          <Bot :size="18" class="text-[var(--icon-secondary)] shrink-0" />
          <span>Agents</span>
        </button>
        <button class="sidebar-nav-item" @click="focusSearchInput">
          <SearchIconLucide :size="18" class="text-[var(--icon-secondary)] shrink-0" />
          <span>Search</span>
        </button>
        <button class="sidebar-nav-item" @click="showInfoToast('Library coming soon')">
          <Library :size="18" class="text-[var(--icon-secondary)] shrink-0" />
          <span>Library</span>
        </button>

        <div v-if="showSearchInput || searchQuery" class="px-[4px] py-2">
          <input
            ref="searchInputRef"
            v-model="searchQuery"
            type="text"
            placeholder="Search tasks"
            class="w-full h-9 rounded-[10px] border border-[var(--border-main)] bg-[var(--background-white-main)] px-3 text-sm outline-none" />
        </div>

        <div class="mx-2 my-2 border-t border-[var(--border-main)]"></div>

        <div class="flex items-center justify-between px-[10px] py-[8px]">
          <span class="text-[13px] leading-[18px] text-[var(--text-tertiary)] font-medium">Projects</span>
          <button class="flex h-7 w-7 items-center justify-center rounded-md hover:bg-[var(--fill-tsp-white-light)]" @click="createProject">
            <Plus :size="16" class="text-[var(--icon-secondary)]" />
          </button>
        </div>

        <button class="sidebar-nav-item !h-[34px]" @click="createProject">
          <Folder :size="18" class="text-[var(--icon-secondary)] shrink-0" />
          <span>New project</span>
        </button>

        <div v-if="projects.length > 0" class="flex flex-col gap-1 px-[4px] py-1">
          <div v-for="project in filteredProjects" :key="project.id" class="rounded-[12px]">
            <div class="flex items-center gap-2 px-[8px] h-[34px] rounded-[10px] hover:bg-[var(--fill-tsp-white-light)]">
              <button class="flex flex-1 items-center gap-2 min-w-0" @click="toggleProject(project.id)">
                <FolderOpen v-if="expandedProjects[project.id]" :size="16" class="text-[var(--icon-secondary)] shrink-0" />
                <Folder v-else :size="16" class="text-[var(--icon-secondary)] shrink-0" />
                <span class="truncate text-[13px] text-[var(--text-primary)]">{{ project.name }}</span>
                <span class="text-[11px] text-[var(--text-tertiary)]">{{ projectSessionCount(project.id) }}</span>
              </button>
              <button class="flex h-6 w-6 items-center justify-center rounded-md hover:bg-[var(--fill-tsp-white-main)]" @click="addCurrentTaskToProject(project.id)">
                <Plus :size="14" class="text-[var(--icon-secondary)]" />
              </button>
            </div>
            <div v-if="expandedProjects[project.id]" class="pl-2">
              <SessionItem
                v-for="session in sessionsForProject(project.id)"
                :key="session.session_id"
                :session="session"
                @deleted="handleSessionDeleted" />
            </div>
          </div>
        </div>

        <div class="mx-2 my-2 border-t border-[var(--border-main)]"></div>

        <div class="flex flex-col flex-1 min-h-0 overflow-hidden">
          <div class="flex items-center justify-between px-[10px] py-[8px]">
            <span class="text-[13px] leading-[18px] text-[var(--text-tertiary)] font-medium">All Tasks</span>
            <button class="flex items-center gap-1 h-7 px-2 rounded-md hover:bg-[var(--fill-tsp-white-light)]" @click="cycleSortMode">
              <ArrowUpDown :size="14" class="text-[var(--icon-secondary)]" />
              <span class="text-[11px] text-[var(--text-tertiary)] uppercase">{{ sortMode }}</span>
            </button>
          </div>

          <div ref="scrollContainerRef" class="flex flex-col flex-1 min-h-0 overflow-y-auto overflow-x-hidden pb-4 px-[4px]" @scroll="handleListScroll">
            <div v-if="visibleSessions.length > 0" class="flex flex-col gap-px">
              <SessionItem
                v-for="session in visibleSessions"
                :key="session.session_id"
                :session="session"
                @deleted="handleSessionDeleted" />
            </div>
            <div v-else class="flex flex-col items-center justify-center gap-3 py-8 text-[var(--text-tertiary)]">
              <MessageSquareDashed :size="32" />
              <span class="text-sm font-medium">{{ searchQuery ? 'No matching tasks' : 'Create a task to get started' }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="mt-auto border-t border-[var(--border-main)] px-[10px] py-[10px] flex items-center justify-between">
        <button class="flex h-8 w-8 items-center justify-center rounded-md hover:bg-[var(--fill-tsp-white-light)]" @click="openSettingsDialog('settings')">
          <Settings2 :size="16" class="text-[var(--icon-secondary)]" />
        </button>
        <div class="flex items-center gap-1">
          <button class="flex h-8 w-8 items-center justify-center rounded-md hover:bg-[var(--fill-tsp-white-light)]" @click="showInfoToast('List view active')">
            <Rows3 :size="16" class="text-[var(--icon-secondary)]" />
          </button>
          <button class="flex h-8 w-8 items-center justify-center rounded-md hover:bg-[var(--fill-tsp-white-light)]" @click="showInfoToast('Board view coming soon')">
            <Columns2 :size="16" class="text-[var(--icon-secondary)]" />
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import {
  PanelLeft,
  SquarePen,
  MessageSquareDashed,
  Bot,
  Search as SearchIconLucide,
  Library,
  Folder,
  FolderOpen,
  Plus,
  ArrowUpDown,
  Bell,
  Settings2,
  Rows3,
  Columns2,
} from 'lucide-vue-next';
import SessionItem from './SessionItem.vue';
import { useLeftPanel } from '../composables/useLeftPanel';
import { ref, onMounted, watch, onUnmounted, computed, nextTick, reactive } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { getSessionsSSE, getSessions } from '../api/agent';
import { ListSessionItem } from '../types/response';
import { showInfoToast } from '../utils/toast';
import { useSettingsDialog } from '../composables/useSettingsDialog';

interface ProjectItem {
  id: string;
  name: string;
  sessionIds: string[];
}

const { isLeftPanelShow, toggleLeftPanel } = useLeftPanel();
const { openSettingsDialog } = useSettingsDialog();
const route = useRoute();
const router = useRouter();

const sessions = ref<ListSessionItem[]>([]);
const cancelGetSessionsSSE = ref<(() => void) | null>(null);
const scrollContainerRef = ref<HTMLElement | null>(null);
const searchInputRef = ref<HTMLInputElement | null>(null);
const searchQuery = ref('');
const showSearchInput = ref(false);
const sortMode = ref<'date' | 'name'>('date');
const expandedProjects = reactive<Record<string, boolean>>({});
const projects = ref<ProjectItem[]>([]);

const PROJECTS_KEY = 'forge-projects-v1';

const panelStyle = computed(() => (
  isLeftPanelShow.value
    ? 'width: 300px; transition: width 0.28s cubic-bezier(0.4, 0, 0.2, 1);'
    : 'width: 24px; transition: width 0.36s cubic-bezier(0.4, 0, 0.2, 1);'
));

const innerPanelStyle = computed(() => (
  `${isLeftPanelShow.value ? 'width: 300px;' : 'width: 0px;'} transition: opacity 0.2s, transform 0.2s, width 0.2s;`
));

const currentSessionId = computed(() => String(route.params.sessionId || ''));

const normalize = (value: string | null | undefined) => (value || '').toLowerCase();

const matchesSearch = (session: ListSessionItem) => {
  const query = searchQuery.value.trim().toLowerCase();
  if (!query) return true;
  return normalize(session.title).includes(query) || normalize(session.latest_message).includes(query);
};

const sortSessions = (items: ListSessionItem[]) => {
  return [...items].sort((a, b) => {
    if (sortMode.value === 'name') {
      return (a.title || '').localeCompare(b.title || '');
    }
    return (b.latest_message_at || 0) - (a.latest_message_at || 0);
  });
};

const unassignedSessions = computed(() => {
  const assigned = new Set(projects.value.flatMap((project) => project.sessionIds));
  return sessions.value.filter((session) => !assigned.has(session.session_id));
});

const visibleSessions = computed(() => sortSessions(unassignedSessions.value.filter(matchesSearch)));

const filteredProjects = computed(() => {
  return projects.value.filter((project) => sessionsForProject(project.id).length > 0 || !searchQuery.value.trim());
});

const projectSessionCount = (projectId: string) => sessionsForProject(projectId).length;

const sessionsForProject = (projectId: string) => {
  const project = projects.value.find((item) => item.id === projectId);
  if (!project) return [];
  return sortSessions(
    sessions.value.filter((session) => project.sessionIds.includes(session.session_id)).filter(matchesSearch)
  );
};

const saveProjects = () => {
  localStorage.setItem(PROJECTS_KEY, JSON.stringify(projects.value));
};

const loadProjects = () => {
  try {
    const raw = localStorage.getItem(PROJECTS_KEY);
    projects.value = raw ? JSON.parse(raw) : [];
    for (const project of projects.value) {
      if (!(project.id in expandedProjects)) {
        expandedProjects[project.id] = true;
      }
    }
  } catch {
    projects.value = [];
  }
};

const createProject = () => {
  const name = window.prompt('Project name');
  if (!name || !name.trim()) return;
  const project: ProjectItem = {
    id: `${Date.now()}`,
    name: name.trim(),
    sessionIds: currentSessionId.value ? [currentSessionId.value] : [],
  };
  projects.value = [project, ...projects.value];
  expandedProjects[project.id] = true;
  saveProjects();
};

const addCurrentTaskToProject = (projectId: string) => {
  if (!currentSessionId.value) {
    showInfoToast('Open a task first, then add it to a project.');
    return;
  }
  projects.value = projects.value.map((project) => {
    if (project.id !== projectId) return project;
    if (project.sessionIds.includes(currentSessionId.value)) return project;
    return { ...project, sessionIds: [...project.sessionIds, currentSessionId.value] };
  });
  saveProjects();
  showInfoToast('Current task added to project');
};

const toggleProject = (projectId: string) => {
  expandedProjects[projectId] = !expandedProjects[projectId];
};

const focusSearchInput = async () => {
  showSearchInput.value = true;
  await nextTick();
  searchInputRef.value?.focus();
};

const cycleSortMode = () => {
  sortMode.value = sortMode.value === 'date' ? 'name' : 'date';
};

const handleListScroll = () => {
  return;
};

const updateSessions = async () => {
  try {
    const response = await getSessions();
    sessions.value = response.sessions;
  } catch (error) {
    console.error('Failed to fetch sessions:', error);
  }
};

const fetchSessions = async () => {
  try {
    if (cancelGetSessionsSSE.value) {
      cancelGetSessionsSSE.value();
      cancelGetSessionsSSE.value = null;
    }
    cancelGetSessionsSSE.value = await getSessionsSSE({
      onMessage: (event) => {
        sessions.value = event.data.sessions;
      },
      onError: (error) => {
        console.error('Failed to fetch sessions:', error);
      },
    });
  } catch (error) {
    console.error('Failed to fetch sessions:', error);
  }
};

const handleNewTaskClick = () => {
  router.push('/');
};

const handleSessionDeleted = (sessionId: string) => {
  sessions.value = sessions.value.filter((session) => session.session_id !== sessionId);
  projects.value = projects.value.map((project) => ({
    ...project,
    sessionIds: project.sessionIds.filter((id) => id !== sessionId),
  }));
  saveProjects();
};

const handleKeydown = (event: KeyboardEvent) => {
  if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === 'k') {
    event.preventDefault();
    handleNewTaskClick();
  }
};

onMounted(async () => {
  loadProjects();
  fetchSessions();
  window.addEventListener('keydown', handleKeydown);
});

onUnmounted(() => {
  if (cancelGetSessionsSSE.value) {
    cancelGetSessionsSSE.value();
    cancelGetSessionsSSE.value = null;
  }
  window.removeEventListener('keydown', handleKeydown);
});

watch(() => route.path, async () => {
  await updateSessions();
});

watch(projects, () => {
  saveProjects();
}, { deep: true });
</script>

<style scoped>
.sidebar-nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
  height: 36px;
  padding: 0 10px;
  border-radius: 10px;
  color: var(--text-primary);
  font-size: 14px;
  transition: background-color 0.15s ease;
}

.sidebar-nav-item:hover {
  background: var(--fill-tsp-white-light);
}
</style>
