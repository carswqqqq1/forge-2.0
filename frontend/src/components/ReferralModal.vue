<template>
  <Teleport to="body">
    <div v-if="isReferralModalOpen" class="fixed inset-0 z-[88] flex items-center justify-center bg-black/30 backdrop-blur-sm px-4" @click.self="closeReferralModal">
      <div class="w-full max-w-[540px] rounded-[28px] border border-black/5 bg-white p-6 shadow-[0px_30px_80px_0px_rgba(0,0,0,0.18)]">
        <div class="text-3xl">✉️</div>
        <h3 class="mt-3 text-[24px] font-semibold text-[var(--text-primary)]">Invite to get credits</h3>
        <p class="mt-2 text-sm text-[var(--text-secondary)]">Share your invite link with friends, get 500 credits each.</p>

        <div class="mt-5 rounded-[18px] border border-[var(--border-main)] bg-[var(--background-gray-main)] p-4">
          <div class="flex items-center justify-between gap-3">
            <div class="truncate text-sm text-[var(--text-primary)]">{{ referral?.invite_link || 'Loading invite link...' }}</div>
            <button class="rounded-full bg-[var(--Button-primary-black)] px-4 py-2 text-sm font-medium text-[var(--text-onblack)]" @click="copyInvite">
              Copy invitation link
            </button>
          </div>
          <div class="mt-4 flex items-center gap-2 text-sm">
            <button class="social-btn">WhatsApp</button>
            <button class="social-btn">X</button>
            <button class="social-btn">LinkedIn</button>
            <button class="social-btn">Reddit</button>
          </div>
          <div class="mt-4 flex gap-2">
            <input v-model="inviteEmail" class="flex-1 h-11 rounded-[14px] border border-[var(--border-main)] px-4 outline-none" placeholder="Send invitation email" />
            <button class="rounded-[14px] border border-[var(--border-main)] px-4 text-sm font-medium" @click="sendEmail">
              Send
            </button>
          </div>
        </div>

        <div class="mt-5 rounded-[18px] border border-[var(--border-main)] bg-white p-4">
          <div class="text-sm font-medium text-[var(--text-primary)]">Invitations</div>
          <div class="mt-3 grid grid-cols-3 gap-3 text-sm">
            <div><div class="text-[var(--text-tertiary)]">Credits</div><div class="font-semibold">{{ referral?.credits_earned || 0 }}</div></div>
            <div><div class="text-[var(--text-tertiary)]">Referrals</div><div class="font-semibold">{{ referral?.referral_count || 0 }}</div></div>
            <div class="flex items-end justify-end"><button class="rounded-full border border-[var(--border-main)] px-3 py-1.5 text-xs font-medium" @click="showSuccessToast('Referral credits are already applied automatically')">Redeem</button></div>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { getReferralInfo } from '../api/referrals';
import { useReferralModal } from '../composables/useReferralModal';
import { showInfoToast, showSuccessToast } from '../utils/toast';

const { isReferralModalOpen, closeReferralModal } = useReferralModal();
const referral = ref<Awaited<ReturnType<typeof getReferralInfo>> | null>(null);
const inviteEmail = ref('');

const loadReferral = async () => {
  referral.value = await getReferralInfo();
};

const copyInvite = async () => {
  if (!referral.value?.invite_link) return;
  await navigator.clipboard.writeText(referral.value.invite_link);
  showSuccessToast('Invitation link copied');
};

const sendEmail = () => {
  if (!inviteEmail.value.trim()) {
    showInfoToast('Add an email first');
    return;
  }
  showSuccessToast(`Invite prepared for ${inviteEmail.value.trim()}`);
  inviteEmail.value = '';
};

watch(isReferralModalOpen, (open) => {
  if (open) void loadReferral();
});
</script>

<style scoped>
.social-btn {
  border-radius: 9999px;
  border: 1px solid var(--border-main);
  background: white;
  padding: 8px 12px;
}
</style>
