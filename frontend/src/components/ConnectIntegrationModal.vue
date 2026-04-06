<template>
  <Teleport to="body">
    <div v-if="isConnectModalOpen" class="fixed inset-0 z-[85] flex items-center justify-center bg-black/25 backdrop-blur-sm px-4" @click.self="closeConnectModal">
      <div class="w-full max-w-[460px] rounded-[28px] border border-black/5 bg-white shadow-[0px_30px_80px_0px_rgba(0,0,0,0.2)] p-6">
        <div class="flex items-center gap-3">
          <IntegrationLogo :name="activeIntegration" />
          <div>
            <h3 class="text-[20px] font-semibold text-[var(--text-primary)]">Connect {{ activeIntegration }}</h3>
            <p class="text-sm text-[var(--text-secondary)]">{{ description }}</p>
          </div>
        </div>

        <div v-if="activeIntegration === 'GitHub'" class="mt-5 space-y-3">
          <label class="block text-sm font-medium text-[var(--text-primary)]">GitHub personal access token</label>
          <input
            v-model="githubToken"
            type="password"
            placeholder="ghp_..."
            class="w-full h-11 rounded-[14px] border border-[var(--border-main)] px-4 outline-none" />
          <div class="flex gap-3">
            <button class="rounded-[14px] bg-[var(--Button-primary-black)] text-[var(--text-onblack)] px-4 py-2 text-sm font-medium" @click="saveGithubToken">
              Connect
            </button>
            <button class="rounded-[14px] border border-[var(--border-main)] px-4 py-2 text-sm font-medium" @click="closeConnectModal">
              Cancel
            </button>
          </div>
        </div>

        <div v-else class="mt-5 space-y-4">
          <div class="rounded-[18px] border border-[var(--border-main)] bg-[var(--background-gray-main)] px-4 py-4 text-sm text-[var(--text-secondary)]">
            Coming soon. We’re building this integration next and can notify you as soon as it’s ready.
          </div>
          <input
            v-model="email"
            type="email"
            placeholder="Email for updates"
            class="w-full h-11 rounded-[14px] border border-[var(--border-main)] px-4 outline-none" />
          <div class="flex gap-3">
            <button class="rounded-[14px] bg-[var(--Button-primary-black)] text-[var(--text-onblack)] px-4 py-2 text-sm font-medium" @click="saveInterest">
              Join waitlist
            </button>
            <button class="rounded-[14px] border border-[var(--border-main)] px-4 py-2 text-sm font-medium" @click="closeConnectModal">
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import { useConnectModal } from '../composables/useConnectModal';
import { showInfoToast, showSuccessToast } from '../utils/toast';
import IntegrationLogo from './IntegrationLogo.vue';

const { isConnectModalOpen, activeIntegration, closeConnectModal } = useConnectModal();
const githubToken = ref(localStorage.getItem('forge-github-token') || '');
const email = ref(localStorage.getItem('forge-integration-email') || '');

const description = computed(() => {
  if (activeIntegration.value === 'GitHub') {
    return 'Connect GitHub so Forge can read repositories and ship changes with you.';
  }
  return `Link ${activeIntegration.value} so Forge can use your real tools inside tasks.`;
});

const saveGithubToken = () => {
  localStorage.setItem('forge-github-token', githubToken.value.trim());
  showSuccessToast('GitHub token saved locally for Forge');
  closeConnectModal();
};

const saveInterest = () => {
  if (!email.value.trim()) {
    showInfoToast('Add an email first so Forge can notify you.');
    return;
  }
  localStorage.setItem('forge-integration-email', email.value.trim());
  showSuccessToast(`Saved your interest for ${activeIntegration.value}`);
  closeConnectModal();
};
</script>
