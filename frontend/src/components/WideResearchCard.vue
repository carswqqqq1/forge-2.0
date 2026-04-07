<template>
  <div class="rounded-[24px] border border-[var(--border-main)] bg-white p-5 shadow-[0px_18px_48px_0px_rgba(0,0,0,0.05)]">
    <div class="flex items-center justify-between gap-3">
      <div class="flex items-center gap-2 text-sm font-medium text-[var(--text-primary)]">
        <span class="inline-flex h-7 w-7 items-center justify-center rounded-full bg-[#dbeafe] text-[#2563eb]">⊕</span>
        <span>Wide Research</span>
      </div>
      <div class="flex items-center gap-2 text-[13px] text-[var(--text-secondary)]">
        <span>{{ completed }}/{{ total }}</span>
        <span>👁</span>
      </div>
    </div>

    <div class="mt-3 text-[18px] font-medium text-[var(--text-primary)]">
      Deep-Dive Research on {{ title || 'your topic' }}
    </div>

    <div v-if="subjects.length" class="mt-4 grid gap-3 md:grid-cols-3">
      <div v-for="subject in subjects" :key="subject.name" class="rounded-[18px] border border-[var(--border-main)] bg-[var(--background-gray-main)] px-4 py-3">
        <div class="flex items-center justify-between gap-2">
          <div class="truncate text-sm font-medium text-[var(--text-primary)]">{{ subject.name }}</div>
          <span class="text-xs" :class="statusColor(subject.status)">
            {{ statusIcon(subject.status) }}
          </span>
        </div>
        <div class="mt-2 text-[12px] text-[var(--text-secondary)]">{{ statusLabel(subject.status) }}</div>
      </div>
    </div>

    <div class="mt-4 flex items-center justify-between gap-3 flex-wrap text-[13px] text-[var(--text-secondary)]">
      <span>Wide Research will cost credits for {{ total || 0 }} subtasks.</span>
      <div class="flex items-center gap-3">
        <button class="text-[var(--text-secondary)] underline" @click="$emit('continue-normal')">continue without Wide Research</button>
        <button v-if="showSkip" class="rounded-full border border-[var(--border-main)] px-4 py-2" @click="$emit('skip')">Skip</button>
        <button class="rounded-full bg-[var(--Button-primary-black)] px-4 py-2 text-sm text-white" :disabled="started">
          {{ started ? 'Running' : 'Start' }}
        </button>
      </div>
    </div>

    <div v-if="rows.length" class="mt-5 overflow-hidden rounded-[18px] border border-[var(--border-main)]">
      <table class="w-full text-left text-[12px]">
        <thead class="bg-[var(--background-gray-main)] text-[var(--text-secondary)]">
          <tr>
            <th class="px-3 py-2">Subject</th>
            <th class="px-3 py-2">Description</th>
            <th class="px-3 py-2">Key Capabilities</th>
            <th class="px-3 py-2">Pricing</th>
            <th class="px-3 py-2">Pros/Cons</th>
            <th class="px-3 py-2">USP</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in rows" :key="row.name" class="border-t border-[var(--border-main)] align-top">
            <td class="px-3 py-2 font-medium text-[var(--text-primary)]">{{ row.name }}</td>
            <td class="px-3 py-2 text-[var(--text-secondary)]">{{ row.description }}</td>
            <td class="px-3 py-2 text-[var(--text-secondary)]">{{ joinList(row.capabilities) }}</td>
            <td class="px-3 py-2 text-[var(--text-secondary)]">{{ row.pricing }}</td>
            <td class="px-3 py-2 text-[var(--text-secondary)]">{{ prosCons(row) }}</td>
            <td class="px-3 py-2 text-[var(--text-secondary)]">{{ row.usp }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
type ResearchSubjectCard = {
  name: string;
  status: 'waiting' | 'running' | 'completed' | 'skipped';
};

defineProps<{
  title: string;
  subjects: ResearchSubjectCard[];
  completed: number;
  total: number;
  started: boolean;
  showSkip: boolean;
  rows: Array<Record<string, any>>;
}>();

defineEmits<{
  (e: 'continue-normal'): void;
  (e: 'skip'): void;
}>();

const statusIcon = (status: string) => {
  if (status === 'completed') return '✓';
  if (status === 'running') return '◔';
  if (status === 'skipped') return '↷';
  return '●';
};

const statusLabel = (status: string) => {
  if (status === 'completed') return 'Completed';
  if (status === 'running') return 'Researching...';
  if (status === 'skipped') return 'Skipped';
  return 'Waiting';
};

const statusColor = (status: string) => {
  if (status === 'completed') return 'text-[#16a34a]';
  if (status === 'running') return 'text-[#2563eb] animate-pulse';
  if (status === 'skipped') return 'text-[#f59e0b]';
  return 'text-black/30';
};

const joinList = (value: unknown) => Array.isArray(value) ? value.join(', ') : String(value || '');
const prosCons = (row: Record<string, any>) => {
  const pros = Array.isArray(row.pros_cons?.pros) ? row.pros_cons.pros.join(', ') : '';
  const cons = Array.isArray(row.pros_cons?.cons) ? row.pros_cons.cons.join(', ') : '';
  return [pros && `Pros: ${pros}`, cons && `Cons: ${cons}`].filter(Boolean).join(' • ');
};
</script>
