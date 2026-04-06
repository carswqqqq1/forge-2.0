import { ref } from 'vue';

export type IntegrationName =
  | 'Notion'
  | 'Gmail'
  | 'Google Calendar'
  | 'GitHub'
  | 'Slack'
  | 'Database'
  | 'Browser';

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
