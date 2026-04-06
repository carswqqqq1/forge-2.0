<template>
  <span class="inline-flex items-center justify-center w-5 h-5" v-html="svg"></span>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import type { IntegrationName } from '../composables/useConnectModal';

const props = defineProps<{
  name: IntegrationName;
}>();

const svg = computed(() => {
  const logos: Record<IntegrationName, string> = {
    Notion: `<svg viewBox="0 0 24 24" width="20" height="20" fill="none"><rect x="2.5" y="2.5" width="19" height="19" rx="3.5" fill="white" stroke="#111827" stroke-width="1.5"/><path d="M8 7.8v8.4h1.7V11l4.6 5.2h1.7V7.8h-1.7v5.1L9.7 7.8H8z" fill="#111827"/></svg>`,
    Gmail: `<svg viewBox="0 0 24 24" width="20" height="20" fill="none"><rect x="2" y="4" width="20" height="16" rx="3" fill="white"/><path d="M4.5 18.5V7.2l7.5 5.6 7.5-5.6v11.3" stroke="#EA4335" stroke-width="2"/><path d="M4.5 7.2 12 12.8l7.5-5.6" stroke="#FBBC05" stroke-width="2"/><path d="M4.5 18.5V7.2" stroke="#34A853" stroke-width="2"/><path d="M19.5 18.5V7.2" stroke="#4285F4" stroke-width="2"/></svg>`,
    'Google Calendar': `<svg viewBox="0 0 24 24" width="20" height="20" fill="none"><rect x="4" y="5" width="16" height="15" rx="3" fill="white" stroke="#DADCE0"/><path d="M8 3v4M16 3v4" stroke="#4285F4" stroke-width="2"/><path d="M4 9h16" stroke="#34A853" stroke-width="2"/><rect x="8" y="11" width="8" height="6" rx="1.5" fill="#4285F4"/><path d="M11 15.4h2.2" stroke="white" stroke-width="1.6" stroke-linecap="round"/></svg>`,
    GitHub: `<svg viewBox="0 0 24 24" width="20" height="20" fill="none"><path d="M12 2.7a9.3 9.3 0 0 0-2.94 18.12c.47.09.64-.2.64-.45 0-.22-.01-.95-.01-1.72-2.35.43-2.96-.58-3.15-1.1-.1-.27-.53-1.1-.91-1.32-.31-.17-.75-.6-.01-.61.7-.01 1.19.64 1.36.91.8 1.34 2.08.96 2.59.73.08-.58.31-.96.56-1.18-2.08-.24-4.25-1.04-4.25-4.61 0-1.02.37-1.86.96-2.52-.1-.24-.42-1.21.09-2.53 0 0 .79-.25 2.58.96a8.9 8.9 0 0 1 4.7 0c1.79-1.22 2.58-.96 2.58-.96.51 1.32.19 2.29.09 2.53.6.66.96 1.49.96 2.52 0 3.58-2.18 4.37-4.26 4.61.33.28.62.82.62 1.66 0 1.2-.01 2.16-.01 2.46 0 .25.17.55.64.45A9.3 9.3 0 0 0 12 2.7Z" fill="#111827"/></svg>`,
    Slack: `<svg viewBox="0 0 24 24" width="20" height="20" fill="none"><path d="M9.6 3.5a2.1 2.1 0 1 1 4.2 0v2.1H9.6V3.5Z" fill="#36C5F0"/><path d="M15.8 9.6a2.1 2.1 0 1 1 0 4.2h-2.1V9.6h2.1Z" fill="#2EB67D"/><path d="M14.4 20.5a2.1 2.1 0 1 1-4.2 0v-2.1h4.2v2.1Z" fill="#ECB22E"/><path d="M8.2 14.4a2.1 2.1 0 1 1 0-4.2h2.1v4.2H8.2Z" fill="#E01E5A"/><path d="M5.6 9.6a2.1 2.1 0 1 1 0-4.2h2.1v4.2H5.6Z" fill="#36C5F0"/><path d="M14.4 5.6a2.1 2.1 0 1 1 4.2 0v2.1h-4.2V5.6Z" fill="#2EB67D"/><path d="M18.4 14.4a2.1 2.1 0 1 1 0 4.2h-2.1v-4.2h2.1Z" fill="#ECB22E"/><path d="M9.6 18.4a2.1 2.1 0 1 1-4.2 0v-2.1h4.2v2.1Z" fill="#E01E5A"/></svg>`,
    Database: `<svg viewBox="0 0 24 24" width="20" height="20" fill="none"><ellipse cx="12" cy="6" rx="6.5" ry="3.5" fill="#E8F5E9" stroke="#059669"/><path d="M5.5 6v5c0 1.93 2.91 3.5 6.5 3.5s6.5-1.57 6.5-3.5V6" stroke="#059669" stroke-width="1.5"/><path d="M5.5 11v5c0 1.93 2.91 3.5 6.5 3.5s6.5-1.57 6.5-3.5v-5" stroke="#059669" stroke-width="1.5"/></svg>`,
    Browser: `<svg viewBox="0 0 24 24" width="20" height="20" fill="none"><rect x="3" y="4.5" width="18" height="15" rx="4" fill="#EFF6FF" stroke="#2563EB"/><path d="M3 8.5h18" stroke="#2563EB"/><circle cx="7" cy="6.5" r="1" fill="#2563EB"/><circle cx="10" cy="6.5" r="1" fill="#60A5FA"/><path d="M12 10.5a4 4 0 1 0 0 8 4 4 0 0 0 0-8Z" stroke="#0284C7"/><path d="M8.5 14.5h7" stroke="#0284C7"/><path d="M12 10.5c1 1.1 1.5 2.45 1.5 4S13 17.4 12 18.5c-1-1.1-1.5-2.45-1.5-4S11 11.6 12 10.5Z" stroke="#0284C7"/></svg>`,
  };
  return logos[props.name];
});
</script>
