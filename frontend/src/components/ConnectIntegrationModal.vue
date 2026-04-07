<template>
  <Teleport to="body">
    <div v-if="isConnectModalOpen" class="fixed inset-0 z-[85] flex items-center justify-center bg-black/25 backdrop-blur-sm px-4" @click.self="closeConnectModal">
      <div class="w-full max-w-[560px] rounded-[28px] border border-black/5 bg-white shadow-[0px_30px_80px_0px_rgba(0,0,0,0.2)] p-6">
        <div class="flex items-center gap-3">
          <IntegrationLogo :name="activeIntegration" />
          <div>
            <h3 class="text-[20px] font-semibold text-[var(--text-primary)]">{{ activeIntegration }}</h3>
            <p class="text-sm text-[var(--text-secondary)]">{{ description }}</p>
          </div>
        </div>

        <div class="mt-5 rounded-[18px] border border-[var(--border-main)] bg-[var(--background-gray-main)] p-4">
          <div class="text-sm font-medium text-[var(--text-primary)]">Connector details</div>
          <div class="mt-3 grid grid-cols-[140px_1fr] gap-y-2 text-sm">
            <span class="text-[var(--text-tertiary)]">Connector Type</span><span>{{ connectorType }}</span>
            <span class="text-[var(--text-tertiary)]">Author</span><span>Forge</span>
            <span class="text-[var(--text-tertiary)]">UUID</span><span class="truncate">{{ connectorId }}</span>
            <span class="text-[var(--text-tertiary)]">Website</span><span>forge.local/connectors</span>
          </div>
        </div>

        <div v-if="activeIntegration === 'GitHub'" class="mt-5 space-y-3">
          <div class="rounded-[18px] border border-[var(--border-main)] bg-[var(--background-gray-main)] p-4 text-sm text-[var(--text-secondary)]">
            Forge will redirect you to GitHub so you can authorize repo, user, and org access securely with OAuth.
          </div>
        </div>

        <div class="mt-5 flex flex-wrap gap-3">
          <button class="rounded-[14px] bg-[var(--Button-primary-black)] text-[var(--text-onblack)] px-4 py-2 text-sm font-medium" @click="handleConnect">
            {{ activeIntegration === 'GitHub' ? '+ Connect' : 'Try it out' }}
          </button>
          <button class="rounded-[14px] border border-[var(--border-main)] px-4 py-2 text-sm font-medium" @click="showManage = !showManage">
            Manage
          </button>
          <button class="rounded-[14px] border border-[var(--border-main)] px-4 py-2 text-sm font-medium" @click="closeConnectModal">
            Close
          </button>
        </div>

        <div v-if="showManage" class="mt-4 rounded-[18px] border border-[var(--border-main)] p-3">
          <button class="manage-row" @click="showInfoToast('Connector configuration is coming soon')">Configure</button>
          <button class="manage-row text-[#dc2626]" @click="handleDisconnect">Disconnect</button>
        </div>

        <button class="mt-4 text-sm text-[var(--text-secondary)]" @click="showInfoToast('Feedback capture is coming soon')">Provide feedback</button>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import { useConnectModal } from '../composables/useConnectModal';
import { showInfoToast, showSuccessToast } from '../utils/toast';
import IntegrationLogo from './IntegrationLogo.vue';
import { connectConnector, disconnectConnector } from '../api/connectors';

const { isConnectModalOpen, activeIntegration, closeConnectModal } = useConnectModal();
const showManage = ref(false);

const connectorMap: Record<string, { id: string; type: string }> = {
  'My Browser': { id: 'my-browser', type: 'app' },
  Notion: { id: 'notion', type: 'app' },
  Gmail: { id: 'gmail', type: 'app' },
  'Google Calendar': { id: 'google-calendar', type: 'app' },
  'Google Drive': { id: 'google-drive', type: 'app' },
  'Outlook Mail': { id: 'outlook-mail', type: 'app' },
  'Outlook Calendar': { id: 'outlook-calendar', type: 'app' },
  GitHub: { id: 'github', type: 'app' },
  Instagram: { id: 'instagram', type: 'app' },
  'Meta Ads Manager': { id: 'meta-ads-manager', type: 'app' },
  Slack: { id: 'slack', type: 'app' },
  Zapier: { id: 'zapier', type: 'app' },
  Asana: { id: 'asana', type: 'app' },
  'monday.com': { id: 'monday', type: 'app' },
  Make: { id: 'make', type: 'app' },
  Linear: { id: 'linear', type: 'app' },
  Atlassian: { id: 'atlassian', type: 'app' },
  ClickUp: { id: 'clickup', type: 'app' },
  Supabase: { id: 'supabase', type: 'app' },
  Vercel: { id: 'vercel', type: 'app' },
  Neon: { id: 'neon', type: 'app' },
  'Prisma Postgres': { id: 'prisma-postgres', type: 'app' },
  Sentry: { id: 'sentry', type: 'app' },
  'Hugging Face': { id: 'hugging-face', type: 'app' },
  HubSpot: { id: 'hubspot', type: 'app' },
  Intercom: { id: 'intercom', type: 'app' },
  Stripe: { id: 'stripe', type: 'app' },
  'PayPal for Business': { id: 'paypal-business', type: 'app' },
  RevenueCat: { id: 'revenuecat', type: 'app' },
  Close: { id: 'close', type: 'app' },
  Xero: { id: 'xero', type: 'app' },
  Airtable: { id: 'airtable', type: 'app' },
  'Google Drive File Picker': { id: 'google-drive-file-picker', type: 'app' },
  Database: { id: 'custom-api', type: 'custom_api' },
  Browser: { id: 'my-browser', type: 'app' },
  'Custom API': { id: 'custom-api', type: 'custom_api' },
  'Custom MCP': { id: 'custom-mcp', type: 'custom_mcp' },
};

const connectorId = computed(() => connectorMap[activeIntegration.value]?.id || 'custom-api');
const connectorType = computed(() => connectorMap[activeIntegration.value]?.type || 'app');

const description = computed(() => {
  if (activeIntegration.value === 'GitHub') {
    return 'Connect GitHub so Forge can read repositories and ship changes with you.';
  }
  return `Link ${activeIntegration.value} so Forge can use your real tools inside tasks.`;
});

const handleConnect = async () => {
  const payload = { metadata: { label: activeIntegration.value }, type: connectorType.value };
  const result = await connectConnector(connectorId.value, payload);
  if (result.oauth_url) {
    window.location.href = result.oauth_url;
    return;
  }
  showSuccessToast(`Successfully connected ${activeIntegration.value}`);
  closeConnectModal();
};

const handleDisconnect = async () => {
  await disconnectConnector(connectorId.value);
  showSuccessToast(`Successfully disconnected ${activeIntegration.value}`);
  closeConnectModal();
};
</script>

<style scoped>
.manage-row {
  display: block;
  width: 100%;
  text-align: left;
  border-radius: 12px;
  padding: 10px 12px;
}

.manage-row:hover {
  background: var(--fill-tsp-white-light);
}
</style>
