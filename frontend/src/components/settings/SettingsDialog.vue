<template>
  <Dialog v-model:open="isSettingsDialogOpen">
    <DialogContent class="w-[95vw] max-w-[1120px] p-0 overflow-hidden">
      <div class="flex h-[80vh] max-h-[820px] bg-white settings-shell">
        <aside class="w-[250px] border-r border-[var(--border-main)] bg-[var(--background-gray-main)] px-3 py-4 overflow-y-auto">
          <div class="px-3 pb-4">
            <div class="text-[18px] font-semibold text-[var(--text-primary)]">Settings</div>
            <div class="mt-1 text-[13px] text-[var(--text-tertiary)]">Manage your Forge workspace</div>
          </div>
          <button
            v-for="item in sections"
            :key="item.id"
            class="settings-nav-btn"
            :class="activeSection === item.id ? 'settings-nav-btn--active' : ''"
            @click="activeSection = item.id">
            <component :is="item.icon" :size="16" />
            <span>{{ item.label }}</span>
          </button>
        </aside>

        <section class="flex-1 overflow-y-auto px-6 py-6">
          <div class="mb-6 flex items-center justify-between gap-3">
            <div>
              <h2 class="text-[24px] font-semibold text-[var(--text-primary)]">{{ currentSection?.label }}</h2>
              <p class="mt-1 text-sm text-[var(--text-secondary)]">{{ sectionDescription }}</p>
            </div>
            <button class="rounded-full border border-[var(--border-main)] px-4 py-2 text-sm font-medium" @click="closeSettingsDialog">
              Close
            </button>
          </div>

          <template v-if="activeSection === 'account'">
            <div class="rounded-[24px] border border-[var(--border-main)] bg-white p-5">
              <div class="flex items-start justify-between gap-5">
                <div class="flex items-center gap-4">
                  <div class="flex h-16 w-16 items-center justify-center rounded-full bg-[#3b82f6] text-xl font-semibold text-white">
                    {{ avatarLetter }}
                  </div>
                  <div>
                    <div class="text-[18px] font-semibold text-[var(--text-primary)]">{{ account.fullname }}</div>
                    <div class="text-sm text-[var(--text-secondary)]">{{ account.email }}</div>
                    <div class="mt-2 inline-flex items-center rounded-full bg-[var(--background-gray-main)] px-3 py-1 text-xs font-medium text-[var(--text-primary)]">
                      {{ account.plan_name }}
                    </div>
                  </div>
                </div>
                <div class="flex gap-2">
                  <button class="icon-action-btn" @click="showInfoToast('Avatar customization is coming soon')"><Camera :size="16" /></button>
                  <button class="icon-action-btn" @click="showInfoToast('Profile sharing is coming soon')"><Share2 :size="16" /></button>
                </div>
              </div>

              <div class="mt-5 grid gap-4 md:grid-cols-2">
                <div class="rounded-[20px] border border-[var(--border-main)] bg-[var(--background-gray-main)] p-4">
                  <div class="text-sm font-medium text-[var(--text-primary)]">{{ account.plan_name }}</div>
                  <div class="mt-2 text-sm text-[var(--text-secondary)]">Renews {{ renewalText }}</div>
                  <div class="mt-4 flex gap-2">
                    <button class="primary-btn" @click="showInfoToast('Billing management is coming soon')">Manage</button>
                    <button class="secondary-btn" @click="showInfoToast('Credit top-ups are coming soon')">Add credits</button>
                  </div>
                </div>
                <div class="rounded-[20px] border border-[var(--border-main)] bg-[var(--background-gray-main)] p-4">
                  <div class="flex items-center gap-2 text-sm font-medium text-[var(--text-primary)]">✦ Credits</div>
                  <div class="mt-3 space-y-2 text-sm text-[var(--text-secondary)]">
                    <div class="flex justify-between"><span>Total</span><span class="font-semibold text-[var(--text-primary)]">{{ account.credits }}</span></div>
                    <div class="flex justify-between"><span>Free credits</span><span>{{ account.free_credits }}</span></div>
                    <div class="flex justify-between"><span>Monthly credits</span><span>{{ account.monthly_credits }}/{{ account.monthly_credits_max }}</span></div>
                    <div class="flex justify-between"><span>Daily refresh</span><span>{{ account.daily_refresh_credits }}</span></div>
                  </div>
                  <div class="mt-3 text-xs text-[var(--text-tertiary)]">Refresh to {{ account.monthly_credits_max }} at 00:00 every day</div>
                </div>
              </div>
            </div>
          </template>

          <template v-else-if="activeSection === 'settings'">
            <div class="space-y-5">
              <div class="rounded-[24px] border border-[var(--border-main)] bg-white p-5">
                <label class="text-sm font-medium text-[var(--text-primary)]">Language</label>
                <select v-model="settingsForm.preferred_language" class="mt-2 h-11 w-full rounded-[14px] border border-[var(--border-main)] px-4">
                  <option>English</option>
                </select>
              </div>
              <div class="rounded-[24px] border border-[var(--border-main)] bg-white p-5">
                <div class="text-sm font-medium text-[var(--text-primary)]">Appearance</div>
                <div class="mt-3 grid grid-cols-3 gap-3">
                  <button v-for="appearance in ['light', 'dark', 'system']" :key="appearance" class="appearance-card" :class="settingsForm.appearance === appearance ? 'appearance-card--active' : ''" @click="settingsForm.appearance = appearance">
                    <div class="appearance-preview" :class="`appearance-preview--${appearance}`"></div>
                    <span class="capitalize">{{ appearance === 'system' ? 'Follow System' : appearance }}</span>
                  </button>
                </div>
              </div>
              <div class="rounded-[24px] border border-[var(--border-main)] bg-white p-5">
                <div class="space-y-4">
                  <label class="flex items-center justify-between text-sm text-[var(--text-primary)]"><span>Receive product updates</span><input v-model="settingsForm.receive_product_updates" type="checkbox" /></label>
                  <label class="flex items-center justify-between text-sm text-[var(--text-primary)]"><span>Email me when my queued task starts</span><input v-model="settingsForm.email_when_queued_task_starts" type="checkbox" /></label>
                </div>
                <div class="mt-5 flex gap-2">
                  <button class="primary-btn" @click="saveSettings">Save</button>
                  <button class="secondary-btn" @click="showInfoToast('Cookie controls are coming soon')">Manage Cookies</button>
                </div>
              </div>
            </div>
          </template>

          <template v-else-if="activeSection === 'usage'">
            <div class="rounded-[24px] border border-[var(--border-main)] bg-white p-5">
              <div class="flex items-center justify-between">
                <div class="text-sm font-medium text-[var(--text-primary)]">Usage records</div>
                <button class="text-sm text-[var(--text-secondary)]" @click="activeSection = 'billing'">Website usage & billing ></button>
              </div>
              <div class="mt-4 overflow-hidden rounded-[18px] border border-[var(--border-main)]">
                <div class="grid grid-cols-[1fr_180px_120px] bg-[var(--background-gray-main)] px-4 py-3 text-xs font-medium uppercase tracking-[0.08em] text-[var(--text-tertiary)]">
                  <span>Details</span><span>Date</span><span>Credits</span>
                </div>
                <div v-for="item in usageItems" :key="item.id" class="grid grid-cols-[1fr_180px_120px] px-4 py-3 text-sm border-t border-[var(--border-main)]">
                  <span>{{ item.label }}</span>
                  <span class="text-[var(--text-secondary)]">{{ formatDate(item.created_at) }}</span>
                  <span :class="item.credits_delta >= 0 ? 'text-[#16a34a]' : 'text-[var(--text-primary)]'">{{ item.credits_delta }}</span>
                </div>
              </div>
            </div>
          </template>

          <template v-else-if="activeSection === 'billing'">
            <div class="rounded-[24px] border border-[var(--border-main)] bg-white p-5">
              <div class="text-sm font-medium text-[var(--text-primary)]">Billing Dashboard</div>
              <div class="mt-2 text-sm text-[var(--text-secondary)]">Manage your subscription and credits</div>
              <div class="mt-5 overflow-hidden rounded-[18px] border border-[var(--border-main)]">
                <div class="grid grid-cols-[180px_1fr_120px] bg-[var(--background-gray-main)] px-4 py-3 text-xs font-medium uppercase tracking-[0.08em] text-[var(--text-tertiary)]">
                  <span>Date</span><span>Amount</span><span>Download</span>
                </div>
                <div v-for="item in billingItems" :key="item.id" class="grid grid-cols-[180px_1fr_120px] px-4 py-3 text-sm border-t border-[var(--border-main)]">
                  <span>{{ formatDate(item.created_at) }}</span>
                  <span>{{ item.amount }} {{ item.currency }} · {{ item.label }}</span>
                  <button class="text-left text-[var(--text-secondary)]" @click="showInfoToast('Invoices are coming soon')">Download</button>
                </div>
              </div>
            </div>
          </template>

          <template v-else-if="activeSection === 'scheduled_tasks'">
            <div class="space-y-5">
              <div class="rounded-[24px] border border-[var(--border-main)] bg-white p-5">
                <div class="grid gap-3 md:grid-cols-2">
                  <input v-model="scheduleForm.name" class="h-11 rounded-[14px] border border-[var(--border-main)] px-4" placeholder="Name" />
                  <input v-model="scheduleForm.schedule_text" class="h-11 rounded-[14px] border border-[var(--border-main)] px-4" placeholder="every Monday at 9am" />
                </div>
                <textarea v-model="scheduleForm.description" class="mt-3 min-h-[100px] w-full rounded-[14px] border border-[var(--border-main)] px-4 py-3" placeholder="Description"></textarea>
                <div class="mt-4 flex gap-2">
                  <button class="primary-btn" @click="saveSchedule">{{ scheduleForm.schedule_id ? 'Update schedule' : 'Create schedule' }}</button>
                  <button class="secondary-btn" @click="resetScheduleForm">Clear</button>
                </div>
              </div>

              <div class="rounded-[24px] border border-[var(--border-main)] bg-white p-5">
                <div v-if="schedules.length === 0" class="text-sm text-[var(--text-secondary)]">No scheduled tasks yet.</div>
                <div v-else class="overflow-hidden rounded-[18px] border border-[var(--border-main)]">
                  <div class="grid grid-cols-[1.2fr_1fr_110px_180px_120px] bg-[var(--background-gray-main)] px-4 py-3 text-xs font-medium uppercase tracking-[0.08em] text-[var(--text-tertiary)]">
                    <span>Name</span><span>Schedule</span><span>Status</span><span>Next Run</span><span>Actions</span>
                  </div>
                  <div v-for="item in schedules" :key="item.schedule_id" class="grid grid-cols-[1.2fr_1fr_110px_180px_120px] px-4 py-3 text-sm border-t border-[var(--border-main)]">
                    <span>{{ item.name }}</span>
                    <span class="text-[var(--text-secondary)]">{{ item.schedule_text }}</span>
                    <span class="capitalize">{{ item.status }}</span>
                    <span class="text-[var(--text-secondary)]">{{ item.next_run ? formatDate(item.next_run) : '—' }}</span>
                    <div class="flex gap-2">
                      <button @click="editSchedule(item)">Edit</button>
                      <button class="text-[#dc2626]" @click="removeSchedule(item.schedule_id)">Delete</button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </template>

          <template v-else-if="activeSection === 'personalization'">
            <div class="rounded-[24px] border border-[var(--border-main)] bg-white p-5">
              <div class="flex gap-2">
                <button class="rounded-full border px-3 py-1.5 text-sm" :class="personalizationTab === 'profile' ? 'bg-[var(--Button-primary-black)] text-[var(--text-onblack)] border-[var(--Button-primary-black)]' : 'border-[var(--border-main)]'" @click="personalizationTab = 'profile'">Profile</button>
                <button class="rounded-full border px-3 py-1.5 text-sm" :class="personalizationTab === 'knowledge' ? 'bg-[var(--Button-primary-black)] text-[var(--text-onblack)] border-[var(--Button-primary-black)]' : 'border-[var(--border-main)]'" @click="personalizationTab = 'knowledge'">Knowledge</button>
              </div>
              <div class="mt-4 grid gap-3">
                <input v-model="profileForm.nickname" class="h-11 rounded-[14px] border border-[var(--border-main)] px-4" placeholder="Nickname" />
                <input v-model="profileForm.occupation" class="h-11 rounded-[14px] border border-[var(--border-main)] px-4" placeholder="Occupation" />
                <textarea v-model="profileForm.more_about_you" class="min-h-[130px] rounded-[14px] border border-[var(--border-main)] px-4 py-3" maxlength="2000" placeholder="More about you"></textarea>
                <textarea v-model="profileForm.custom_instructions" class="min-h-[150px] rounded-[14px] border border-[var(--border-main)] px-4 py-3" maxlength="3000" placeholder="Custom Instructions"></textarea>
              </div>
              <div class="mt-4 flex gap-2">
                <button class="secondary-btn" @click="loadAccountSummary">Cancel</button>
                <button class="primary-btn" @click="saveProfile">Save</button>
              </div>
            </div>
          </template>

          <template v-else-if="activeSection === 'connectors'">
            <div class="space-y-5">
              <div class="flex items-center justify-between">
                <button class="primary-btn" @click="showMarketplace = !showMarketplace">+ Add connectors</button>
              </div>
              <div class="rounded-[24px] border border-[var(--border-main)] bg-white p-5">
                <div class="space-y-3">
                  <button v-for="connector in connectedConnectors" :key="connector.connector_id" class="connector-row" @click="openConnectorModal(connector.name as any)">
                    <div class="flex items-center gap-3 min-w-0">
                      <IntegrationLogo :name="connectorLogoName(connector.name)" />
                      <div class="min-w-0 text-left">
                        <div class="text-sm font-medium text-[var(--text-primary)]">{{ connector.name }}</div>
                        <div class="truncate text-[12px] text-[var(--text-secondary)]">{{ connector.description }}</div>
                      </div>
                    </div>
                    <ChevronRight :size="16" class="text-[var(--icon-secondary)]" />
                  </button>
                  <div v-if="connectedConnectors.length === 0" class="text-sm text-[var(--text-secondary)]">No connectors linked yet.</div>
                </div>
              </div>

              <div v-if="showMarketplace" class="rounded-[24px] border border-[var(--border-main)] bg-white p-5">
                <div class="flex gap-2">
                  <button v-for="tab in ['apps', 'custom_api', 'custom_mcp']" :key="tab" class="rounded-full border px-3 py-1.5 text-sm capitalize" :class="marketTab === tab ? 'bg-[var(--Button-primary-black)] text-[var(--text-onblack)] border-[var(--Button-primary-black)]' : 'border-[var(--border-main)]'" @click="marketTab = tab">
                    {{ tab.replace('_', ' ') }}
                  </button>
                </div>
                <input v-model="connectorSearch" class="mt-4 h-11 w-full rounded-[14px] border border-[var(--border-main)] px-4" placeholder="Search connectors..." />
                <div v-if="marketTab === 'apps'" class="mt-4 grid gap-3 md:grid-cols-2">
                  <button v-for="connector in filteredConnectors" :key="connector.connector_id" class="connector-card" @click="openConnectorModal(connector.name as IntegrationName)">
                    <div class="flex items-center gap-3">
                      <IntegrationLogo :name="connectorLogoName(connector.name)" />
                      <div class="text-left">
                        <div class="text-sm font-medium text-[var(--text-primary)]">{{ connector.name }}</div>
                        <div class="text-[12px] text-[var(--text-secondary)]">{{ connector.description }}</div>
                      </div>
                    </div>
                    <span v-if="connector.status === 'connected'" class="text-[12px] text-[#16a34a]">Connected</span>
                  </button>
                </div>
                <div v-else class="mt-4 space-y-3">
                  <input v-model="customConnectorForm.name" class="h-11 w-full rounded-[14px] border border-[var(--border-main)] px-4" :placeholder="marketTab === 'custom_api' ? 'Name' : 'MCP server name'" />
                  <input v-model="customConnectorForm.url" class="h-11 w-full rounded-[14px] border border-[var(--border-main)] px-4" :placeholder="marketTab === 'custom_api' ? 'Base URL' : 'MCP Server URL'" />
                  <input v-model="customConnectorForm.auth" class="h-11 w-full rounded-[14px] border border-[var(--border-main)] px-4" :placeholder="marketTab === 'custom_api' ? 'API Key / Auth' : 'Description'" />
                  <button class="primary-btn" @click="connectCustomConnector">{{ marketTab === 'custom_api' ? 'Connect Custom API' : 'Connect Custom MCP' }}</button>
                </div>
              </div>
            </div>
          </template>

          <template v-else>
            <div class="rounded-[24px] border border-[var(--border-main)] bg-white p-8 text-sm text-[var(--text-secondary)]">
              {{ currentSection?.label }} is coming soon in Forge.
            </div>
          </template>
        </section>
      </div>
    </DialogContent>
  </Dialog>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import {
  BellRing,
  Bot,
  ChevronRight,
  Cloud,
  CreditCard,
  Database,
  FileCog,
  GraduationCap,
  HelpCircle,
  Link2,
  Mail,
  Shield,
  Share2,
  Sparkles,
  UserRound,
  Camera,
} from 'lucide-vue-next';
import { Dialog, DialogContent } from '@/components/ui/dialog';
import { useSettingsDialog } from '@/composables/useSettingsDialog';
import { getAccountSummary, getBillingItems, getUsageItems, updateAccountProfile, updateAccountSettings } from '@/api/account';
import { createSchedule, deleteSchedule, listSchedules, updateSchedule, type ForgeSchedule } from '@/api/schedules';
import { connectConnector, listConnectors, type ConnectorItem } from '@/api/connectors';
import { useAuth } from '@/composables/useAuth';
import { showInfoToast, showSuccessToast } from '@/utils/toast';
import { useConnectModal, type IntegrationName } from '@/composables/useConnectModal';
import IntegrationLogo from '@/components/IntegrationLogo.vue';

const { isSettingsDialogOpen, defaultTab, closeSettingsDialog } = useSettingsDialog();
const { currentUser } = useAuth();
const { openConnectModal } = useConnectModal();

const sections = [
  { id: 'account', label: 'Account', icon: UserRound },
  { id: 'settings', label: 'Settings', icon: FileCog },
  { id: 'usage', label: 'Usage', icon: Sparkles },
  { id: 'billing', label: 'Billing', icon: CreditCard },
  { id: 'scheduled_tasks', label: 'Scheduled tasks', icon: BellRing },
  { id: 'mail_forge', label: 'Mail Forge', icon: Mail },
  { id: 'data_controls', label: 'Data controls', icon: Shield },
  { id: 'cloud_browser', label: 'Cloud browser', icon: Cloud },
  { id: 'personalization', label: 'Personalization', icon: Bot },
  { id: 'skills', label: 'Skills', icon: GraduationCap },
  { id: 'connectors', label: 'Connectors', icon: Link2 },
  { id: 'integrations', label: 'Integrations', icon: Database },
  { id: 'get_help', label: 'Get help', icon: HelpCircle },
] as const;

const activeSection = ref<string>('account');
const sectionDescription = computed(() => {
  const descriptions: Record<string, string> = {
    account: 'Profile, plan, and credits at a glance.',
    settings: 'Language, appearance, and communication preferences.',
    usage: 'Credit usage and Forge activity records.',
    billing: 'Subscription and billing activity.',
    scheduled_tasks: 'Manage scheduled Forge tasks and next-run previews.',
    personalization: 'Profile and instruction memory for Forge.',
    connectors: 'Connect your tools and data sources.',
  };
  return descriptions[activeSection.value] || 'This section is being expanded for Forge.';
});
const currentSection = computed(() => sections.find((section) => section.id === activeSection.value));

const account = ref({
  id: '',
  fullname: '',
  email: '',
  nickname: '',
  occupation: '',
  more_about_you: '',
  custom_instructions: '',
  plan_name: 'Forge Pro',
  plan_renewal_date: null as string | null,
  credits: 0,
  free_credits: 0,
  monthly_credits: 0,
  monthly_credits_max: 0,
  daily_refresh_credits: 0,
  preferred_language: 'English',
  appearance: 'light',
  receive_product_updates: true,
  email_when_queued_task_starts: true,
});
const usageItems = ref<any[]>([]);
const billingItems = ref<any[]>([]);
const schedules = ref<ForgeSchedule[]>([]);
const connectors = ref<ConnectorItem[]>([]);
const personalizationTab = ref<'profile' | 'knowledge'>('profile');
const showMarketplace = ref(false);
const marketTab = ref<'apps' | 'custom_api' | 'custom_mcp'>('apps');
const connectorSearch = ref('');

const profileForm = ref({
  nickname: '',
  occupation: '',
  more_about_you: '',
  custom_instructions: '',
});

const settingsForm = ref({
  preferred_language: 'English',
  appearance: 'light',
  receive_product_updates: true,
  email_when_queued_task_starts: true,
});

const scheduleForm = ref<Partial<ForgeSchedule>>({
  name: '',
  description: '',
  schedule_text: '',
  status: 'active',
});

const customConnectorForm = ref({
  name: '',
  url: '',
  auth: '',
});

const avatarLetter = computed(() => (account.value.fullname || currentUser.value?.fullname || 'F').charAt(0).toUpperCase());
const renewalText = computed(() => account.value.plan_renewal_date ? new Date(account.value.plan_renewal_date).toLocaleDateString() : 'soon');
const connectedConnectors = computed(() => connectors.value.filter((connector) => connector.status === 'connected'));
const filteredConnectors = computed(() => {
  const query = connectorSearch.value.trim().toLowerCase();
  if (!query) return connectors.value;
  return connectors.value.filter((connector) => `${connector.name} ${connector.description}`.toLowerCase().includes(query));
});

const connectorLogoName = (name: string): IntegrationName => {
  const mapping: Record<string, IntegrationName> = {
    'My Browser': 'My Browser',
    Notion: 'Notion',
    Gmail: 'Gmail',
    'Google Calendar': 'Google Calendar',
    'Google Drive': 'Google Drive',
    'Outlook Mail': 'Outlook Mail',
    'Outlook Calendar': 'Outlook Calendar',
    GitHub: 'GitHub',
    Instagram: 'Instagram',
    'Meta Ads Manager': 'Meta Ads Manager',
    Slack: 'Slack',
    Zapier: 'Zapier',
    Asana: 'Asana',
    'monday.com': 'monday.com',
    Make: 'Make',
    Linear: 'Linear',
    Atlassian: 'Atlassian',
    ClickUp: 'ClickUp',
    Supabase: 'Supabase',
    Vercel: 'Vercel',
    Neon: 'Neon',
    'Prisma Postgres': 'Prisma Postgres',
    Sentry: 'Sentry',
    'Hugging Face': 'Hugging Face',
    HubSpot: 'HubSpot',
    Intercom: 'Intercom',
    Stripe: 'Stripe',
    'PayPal for Business': 'PayPal for Business',
    RevenueCat: 'RevenueCat',
    Close: 'Close',
    Xero: 'Xero',
    Airtable: 'Airtable',
    'Google Drive File Picker': 'Google Drive File Picker',
    Browser: 'Browser',
    Database: 'Database',
    'Custom API': 'Custom API',
    'Custom MCP': 'Custom MCP',
  };
  return mapping[name] || 'Database';
};

const loadAccountSummary = async () => {
  const summary = await getAccountSummary();
  account.value = { ...account.value, ...summary };
  profileForm.value = {
    nickname: summary.nickname || '',
    occupation: summary.occupation || '',
    more_about_you: summary.more_about_you || '',
    custom_instructions: summary.custom_instructions || '',
  };
  settingsForm.value = {
    preferred_language: summary.preferred_language || 'English',
    appearance: summary.appearance || 'light',
    receive_product_updates: summary.receive_product_updates ?? true,
    email_when_queued_task_starts: summary.email_when_queued_task_starts ?? true,
  };
  if (currentUser.value) Object.assign(currentUser.value, summary);
};

const loadSupportData = async () => {
  usageItems.value = await getUsageItems();
  billingItems.value = await getBillingItems();
  schedules.value = await listSchedules();
  connectors.value = await listConnectors();
};

const saveProfile = async () => {
  const summary = await updateAccountProfile(profileForm.value);
  account.value = { ...account.value, ...summary };
  if (currentUser.value) Object.assign(currentUser.value, summary);
  showSuccessToast('Profile saved');
};

const saveSettings = async () => {
  const summary = await updateAccountSettings(settingsForm.value);
  account.value = { ...account.value, ...summary };
  if (currentUser.value) Object.assign(currentUser.value, summary);
  showSuccessToast('Settings saved');
};

const resetScheduleForm = () => {
  scheduleForm.value = { name: '', description: '', schedule_text: '', status: 'active' };
};

const saveSchedule = async () => {
  if (!scheduleForm.value.name || !scheduleForm.value.schedule_text) {
    showInfoToast('Add a name and schedule first');
    return;
  }
  if (scheduleForm.value.schedule_id) {
    await updateSchedule(scheduleForm.value.schedule_id, scheduleForm.value);
    showSuccessToast('Schedule updated');
  } else {
    await createSchedule(scheduleForm.value);
    showSuccessToast('Schedule created');
  }
  schedules.value = await listSchedules();
  resetScheduleForm();
};

const editSchedule = (item: ForgeSchedule) => {
  scheduleForm.value = { ...item };
};

const removeSchedule = async (scheduleId: string) => {
  await deleteSchedule(scheduleId);
  schedules.value = await listSchedules();
  showSuccessToast('Schedule deleted');
};

const connectCustomConnector = async () => {
  if (!customConnectorForm.value.name || !customConnectorForm.value.url) {
    showInfoToast('Add a name and URL first');
    return;
  }
  const connectorId = marketTab.value === 'custom_api' ? 'custom-api' : 'custom-mcp';
  await connectConnector(connectorId, {
    metadata: {
      name: customConnectorForm.value.name,
      url: customConnectorForm.value.url,
      auth: customConnectorForm.value.auth,
    },
    type: marketTab.value === 'custom_api' ? 'custom_api' : 'custom_mcp',
  });
  connectors.value = await listConnectors();
  customConnectorForm.value = { name: '', url: '', auth: '' };
  showSuccessToast('Custom connector saved');
};

const openConnectorModal = (name: IntegrationName) => {
  openConnectModal(name);
};

const formatDate = (value?: string | null) => {
  if (!value) return '—';
  return new Date(value).toLocaleString();
};

watch(isSettingsDialogOpen, async (open) => {
  if (!open) return;
  activeSection.value = defaultTab.value || 'account';
  await loadAccountSummary();
  await loadSupportData();
});
</script>

<style scoped>
.settings-shell {
  animation: slideIn 0.2s ease;
}

.settings-nav-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  padding: 10px 12px;
  border-radius: 14px;
  color: var(--text-secondary);
  font-size: 14px;
  font-weight: 500;
  text-align: left;
}

.settings-nav-btn--active {
  background: white;
  color: var(--text-primary);
  box-shadow: 0 1px 0 rgba(0,0,0,0.03);
}

.icon-action-btn,
.primary-btn,
.secondary-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.icon-action-btn {
  width: 36px;
  height: 36px;
  border-radius: 9999px;
  border: 1px solid var(--border-main);
}

.primary-btn {
  border-radius: 9999px;
  background: var(--Button-primary-black);
  color: var(--text-onblack);
  padding: 10px 16px;
  font-size: 14px;
  font-weight: 500;
}

.secondary-btn {
  border-radius: 9999px;
  border: 1px solid var(--border-main);
  background: white;
  color: var(--text-primary);
  padding: 10px 16px;
  font-size: 14px;
  font-weight: 500;
}

.appearance-card {
  border-radius: 18px;
  border: 1px solid var(--border-main);
  background: white;
  padding: 12px;
  text-align: left;
}

.appearance-card--active {
  border-color: #111827;
  box-shadow: inset 0 0 0 1px #111827;
}

.appearance-preview {
  height: 68px;
  border-radius: 12px;
  margin-bottom: 10px;
}

.appearance-preview--light { background: linear-gradient(135deg, #ffffff, #e5e7eb); }
.appearance-preview--dark { background: linear-gradient(135deg, #0f172a, #334155); }
.appearance-preview--system { background: linear-gradient(135deg, #ffffff 0%, #ffffff 50%, #111827 50%, #111827 100%); }

.connector-row,
.connector-card {
  width: 100%;
  border-radius: 18px;
  border: 1px solid var(--border-main);
  background: white;
  padding: 14px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.connector-card {
  transition: transform 0.18s ease, box-shadow 0.18s ease;
}

.connector-card:hover {
  transform: translateY(-1px);
  box-shadow: 0 12px 28px rgba(0,0,0,0.08);
}

@keyframes slideIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
