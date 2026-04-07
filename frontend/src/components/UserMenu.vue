<template>
  <div class="pointer-events-auto">
    <div class="w-[320px] rounded-[22px] border border-[var(--border-main)] bg-white shadow-[0px_18px_48px_0px_rgba(0,0,0,0.12)] p-3">
      <div class="flex items-start gap-3 px-2 py-2">
        <div class="flex h-12 w-12 items-center justify-center rounded-full bg-[#3b82f6] text-lg font-semibold text-white">
          {{ avatarLetter }}
        </div>
        <div class="min-w-0 flex-1">
          <div class="truncate text-[15px] font-semibold text-[var(--text-primary)]">{{ currentUser?.fullname || 'Forge User' }}</div>
          <div class="truncate text-[13px] text-[var(--text-secondary)]">{{ currentUser?.email || 'No email' }}</div>
        </div>
      </div>

      <div class="mt-2 rounded-[18px] border border-[var(--border-main)] bg-[var(--background-gray-main)] p-3">
        <div class="flex items-center justify-between gap-3">
          <span class="rounded-full bg-white px-3 py-1 text-[12px] font-medium text-[var(--text-primary)]">{{ currentUser?.plan_name || 'Forge Pro' }}</span>
          <button class="text-[12px] font-medium text-[var(--text-primary)]" @click="showInfoToast('Credit top-ups are coming soon')">Add credits</button>
        </div>
        <button class="mt-3 flex w-full items-center justify-between rounded-[14px] bg-white px-3 py-2 text-left" @click="openSettingsDialog('usage')">
          <span class="text-sm text-[var(--text-secondary)]">✦ Credits</span>
          <span class="text-sm font-semibold text-[var(--text-primary)]">{{ currentUser?.credits ?? 0 }} ></span>
        </button>
        <button class="mt-2 flex w-full items-center justify-between rounded-[14px] bg-white px-3 py-2 text-left" @click="showInfoToast('Forge Pro upgrades are coming soon')">
          <span class="text-sm text-[var(--text-primary)]">Explore what's in Forge Pro</span>
          <ChevronRight :size="14" class="text-[var(--icon-secondary)]" />
        </button>
      </div>

      <div class="mt-3 space-y-1">
        <button class="menu-row" @click="openSettingsDialog('personalization')"><Sparkles :size="16" /> <span>Personalization</span></button>
        <button class="menu-row" @click="openSettingsDialog('account')"><User :size="16" /> <span>Account</span></button>
        <button class="menu-row" @click="openSettingsDialog('settings')"><Settings2 :size="16" /> <span>Settings</span></button>
      </div>

      <div class="my-2 h-px bg-[var(--border-main)]"></div>

      <div class="space-y-1">
        <button class="menu-row" @click="openExternal('https://forge-2-0-fsvibxs.netlify.app')"><House :size="16" /> <span>Homepage</span><ExternalLink :size="14" class="ms-auto" /></button>
        <button class="menu-row" @click="showInfoToast('Help center is coming soon')"><LifeBuoy :size="16" /> <span>Get help</span><ExternalLink :size="14" class="ms-auto" /></button>
        <button class="menu-row" @click="showInfoToast('Docs are coming soon')"><BookOpen :size="16" /> <span>Docs</span><ExternalLink :size="14" class="ms-auto" /></button>
      </div>

      <div class="my-2 h-px bg-[var(--border-main)]"></div>

      <button v-if="authProvider !== 'none'" class="menu-row text-[#dc2626]" @click="handleLogout">
        <LogOut :size="16" />
        <span>Sign out</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuth } from '../composables/useAuth';
import { useSettingsDialog } from '../composables/useSettingsDialog';
import { getCachedAuthProvider } from '../api/config';
import { showInfoToast } from '../utils/toast';
import { LogOut, User, Settings2, ExternalLink, ChevronRight, Sparkles, House, LifeBuoy, BookOpen } from 'lucide-vue-next';

const router = useRouter();
const { currentUser, logout } = useAuth();
const { openSettingsDialog } = useSettingsDialog();
const authProvider = ref<string | null>(null);

const avatarLetter = computed(() => currentUser.value?.fullname?.charAt(0)?.toUpperCase() || 'F');

const handleLogout = async () => {
  await logout();
  router.push('/login');
};

const openExternal = (url: string) => {
  window.open(url, '_blank', 'noopener,noreferrer');
};

onMounted(async () => {
  authProvider.value = await getCachedAuthProvider();
});
</script>

<style scoped>
.menu-row {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  padding: 10px 12px;
  border-radius: 14px;
  text-align: left;
  color: var(--text-primary);
}

.menu-row:hover {
  background: var(--fill-tsp-white-light);
}
</style>
