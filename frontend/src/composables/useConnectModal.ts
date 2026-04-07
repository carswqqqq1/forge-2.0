import { ref } from 'vue';

export type IntegrationName =
  | 'My Browser'
  | 'Notion'
  | 'Gmail'
  | 'Google Calendar'
  | 'Google Drive'
  | 'Outlook Mail'
  | 'Outlook Calendar'
  | 'GitHub'
  | 'Instagram'
  | 'Meta Ads Manager'
  | 'Slack'
  | 'Zapier'
  | 'Asana'
  | 'monday.com'
  | 'Make'
  | 'Linear'
  | 'Atlassian'
  | 'ClickUp'
  | 'Supabase'
  | 'Vercel'
  | 'Neon'
  | 'Prisma Postgres'
  | 'Sentry'
  | 'Hugging Face'
  | 'HubSpot'
  | 'Intercom'
  | 'Stripe'
  | 'PayPal for Business'
  | 'RevenueCat'
  | 'Close'
  | 'Xero'
  | 'Airtable'
  | 'Google Drive File Picker'
  | 'Database'
  | 'Browser'
  | 'Custom API'
  | 'Custom MCP';

const isConnectModalOpen = ref(false);
const activeIntegration = ref<IntegrationName>('GitHub');

export function useConnectModal() {
  const openConnectModal = (integration: IntegrationName) => {
    activeIntegration.value = integration;
    isConnectModalOpen.value = true;
  };

  const closeConnectModal = () => {
    isConnectModalOpen.value = false;
  };

  return {
    isConnectModalOpen,
    activeIntegration,
    openConnectModal,
    closeConnectModal,
  };
}
