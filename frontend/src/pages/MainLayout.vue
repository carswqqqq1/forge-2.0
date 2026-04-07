<template>
  <div className="h-screen flex overflow-hidden bg-white">
    <LeftPanel />
    <div className="flex-1 min-w-0 h-full py-0 pr-0 relative">
      <div className="flex h-full bg-[var(--background-gray-main)]">
        <div class="flex flex-1 min-w-0 min-h-0">
          <router-view />
          <FilePanel />
        </div>
      </div>
    </div>
  </div>
  <TakeOverView />
  <CustomDialog />
  <SessionFileList />
  <SettingsDialog />
  <ContextMenu />
  <SearchModal />
  <ConnectIntegrationModal />
  <ReferralModal />
</template>

<script setup lang="ts">
import { watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import LeftPanel from '@/components/LeftPanel.vue';
import CustomDialog from '@/components/ui/CustomDialog.vue';
import ContextMenu from '@/components/ui/ContextMenu.vue';
import TakeOverView from '@/components/TakeOverView.vue';
import SessionFileList from '@/components/SessionFileList.vue';
import FilePanel from '@/components/FilePanel.vue';
import SettingsDialog from '@/components/settings/SettingsDialog.vue';
import SearchModal from '@/components/SearchModal.vue';
import ConnectIntegrationModal from '@/components/ConnectIntegrationModal.vue';
import ReferralModal from '@/components/ReferralModal.vue';
import { showErrorToast, showSuccessToast } from '@/utils/toast';

const route = useRoute();
const router = useRouter();

const formatConnectorName = (value: string) =>
  value
    .split('-')
    .map((part) => (part ? part.charAt(0).toUpperCase() + part.slice(1) : part))
    .join(' ');

watch(
  () => route.query,
  (query) => {
    if (typeof query.connected === 'string') {
      showSuccessToast(`Successfully connected ${formatConnectorName(query.connected)}`);
      const nextQuery = { ...query };
      delete nextQuery.connected;
      delete nextQuery.reason;
      router.replace({ query: nextQuery });
      return;
    }
    if (typeof query.connector_error === 'string') {
      showErrorToast(`Failed to connect ${formatConnectorName(query.connector_error)}`);
      const nextQuery = { ...query };
      delete nextQuery.connector_error;
      delete nextQuery.reason;
      router.replace({ query: nextQuery });
    }
  },
  { immediate: true }
);
</script>
