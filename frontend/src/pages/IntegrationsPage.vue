<template>
  <div class="flex-1 min-w-0 h-full overflow-y-auto bg-[var(--background-gray-main)]">
    <div class="max-w-[980px] mx-auto px-8 py-10">
      <div class="rounded-[30px] border border-[var(--border-main)] bg-white px-8 py-8">
        <h1 class="text-[32px] font-semibold tracking-[-0.03em] text-[var(--text-primary)]">Integrations</h1>
        <p class="mt-3 text-[15px] leading-7 text-[var(--text-secondary)]">
          Forge integrations are coming next. Connect your tools here so research, coding, and execution runs can work across the apps you already use.
        </p>
        <div class="mt-8 grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <div v-for="item in items" :key="item.name" class="rounded-[22px] border border-[var(--border-main)] bg-[var(--background-gray-main)] px-5 py-5">
            <IntegrationLogo :name="item.name" />
            <div class="mt-4 text-[15px] font-semibold text-[var(--text-primary)]">{{ item.name }}</div>
            <div class="mt-2 text-[13px] leading-6 text-[var(--text-secondary)]">{{ item.description }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import IntegrationLogo from '../components/IntegrationLogo.vue';

const items = [
  { name: 'GitHub' as const, description: 'Code context, repos, and publishing.' },
  { name: 'Gmail' as const, description: 'Inbox triage and task-triggered email work.' },
  { name: 'Google Calendar' as const, description: 'Scheduling, prep, and follow-through.' },
  { name: 'Slack' as const, description: 'Work where your team already collaborates.' },
  { name: 'Notion' as const, description: 'Knowledge, docs, and operating procedures.' },
  { name: 'Browser' as const, description: 'Research, automation, and live web actions.' },
];
</script>
