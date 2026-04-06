<template>
  <div class="flex-1 min-w-0 h-full overflow-y-auto bg-[var(--background-gray-main)]">
    <div class="max-w-[1080px] mx-auto px-8 py-10">
      <div class="rounded-[36px] border border-black/5 bg-white px-10 py-10 shadow-[0px_20px_60px_0px_rgba(0,0,0,0.06)]">
        <div class="grid lg:grid-cols-[1.1fr_0.9fr] gap-10 items-center">
          <div>
            <div class="inline-flex items-center gap-2 rounded-full border border-[var(--border-main)] bg-[var(--background-gray-main)] px-3 py-1 text-xs text-[var(--text-secondary)]">
              Deploy Forge where your team already works
            </div>
            <h1 class="mt-5 text-[42px] leading-[1.05] font-semibold tracking-[-0.03em] text-[var(--text-primary)]">
              Deploy your agent for
              <span class="block text-[var(--text-secondary)]">{{ animatedWord }}</span>
            </h1>
            <p class="mt-4 max-w-[560px] text-[15px] leading-7 text-[var(--text-secondary)]">
              Forge gives you a branded, persistent agent that remembers context, runs tasks in the cloud, and meets users across the tools they already use.
            </p>

            <button class="mt-6 inline-flex items-center gap-3 rounded-full bg-[var(--Button-primary-black)] text-[var(--text-onblack)] px-5 py-3 text-sm font-medium">
              <span>Get started</span>
              <div class="flex items-center gap-2 opacity-85">
                <IntegrationLogo name="Slack" />
                <IntegrationLogo name="Browser" />
                <IntegrationLogo name="GitHub" />
              </div>
            </button>
          </div>

          <div class="relative min-h-[320px] rounded-[30px] bg-[linear-gradient(135deg,#f6f5f2_0%,#ffffff_100%)] border border-[var(--border-main)] overflow-hidden">
            <div class="absolute inset-0 opacity-80 bg-[radial-gradient(circle_at_top_left,rgba(59,130,246,0.08),transparent_35%),radial-gradient(circle_at_bottom_right,rgba(34,197,94,0.10),transparent_30%)]"></div>
            <div class="absolute inset-0 flex items-center justify-center">
              <div class="relative w-[260px] h-[220px]">
                <div class="messenger-bubble top-2 left-4 bg-[#229ED9]">TG</div>
                <div class="messenger-bubble top-4 right-10 bg-[#0084FF]">MS</div>
                <div class="messenger-bubble left-12 bottom-10 bg-[#06C755]">LN</div>
                <div class="messenger-bubble right-4 bottom-6 bg-[#25D366]">WA</div>
                <div class="messenger-bubble left-[92px] top-[82px] bg-[#611F69]">SL</div>
                <div class="absolute inset-[56px] rounded-[28px] border border-[var(--border-main)] bg-white shadow-[0px_18px_40px_0px_rgba(0,0,0,0.08)] flex items-center justify-center">
                  <span class="text-[18px] font-semibold lowercase">forge</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="grid md:grid-cols-2 xl:grid-cols-4 gap-4 mt-10">
          <div v-for="card in cards" :key="card.title" class="rounded-[24px] border border-[var(--border-main)] bg-[var(--background-gray-main)] px-5 py-5">
            <component :is="card.icon" :size="20" class="text-[var(--icon-secondary)]" />
            <h3 class="mt-4 text-[15px] font-semibold text-[var(--text-primary)]">{{ card.title }}</h3>
            <p class="mt-2 text-[13px] leading-6 text-[var(--text-secondary)]">{{ card.description }}</p>
          </div>
        </div>

        <div class="mt-10 rounded-[24px] border border-dashed border-[var(--border-main)] px-5 py-5">
          <div class="text-[13px] font-medium uppercase tracking-[0.08em] text-[var(--text-tertiary)]">Coming soon</div>
          <div class="mt-4 flex flex-wrap gap-3">
            <span class="rounded-full border border-[var(--border-main)] px-4 py-2 text-sm text-[var(--text-secondary)]">WhatsApp</span>
            <span class="rounded-full border border-[var(--border-main)] px-4 py-2 text-sm text-[var(--text-secondary)]">Messenger</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue';
import { IdCard, Monitor, Puzzle, MessageCircle } from 'lucide-vue-next';
import IntegrationLogo from '../components/IntegrationLogo.vue';

const words = ['marketing', 'sales', 'support', 'operations'];
const index = ref(0);
let intervalId: number | null = null;

const animatedWord = computed(() => words[index.value]);

const cards = [
  { icon: IdCard, title: 'Brand-consistent AI identity', description: 'Trained on your workflows, integrated with your tools.' },
  { icon: Monitor, title: 'Persistent memory & computer', description: '24/7 cloud assistant that keeps full context and memory.' },
  { icon: Puzzle, title: 'Custom skills', description: 'Equip your assistant with expert knowledge in specific areas.' },
  { icon: MessageCircle, title: 'Works in your messenger', description: 'Available on Telegram, Line, and Slack. More coming soon.' },
];

onMounted(() => {
  intervalId = window.setInterval(() => {
    index.value = (index.value + 1) % words.length;
  }, 2200);
});

onUnmounted(() => {
  if (intervalId) window.clearInterval(intervalId);
});
</script>

<style scoped>
.messenger-bubble {
  position: absolute;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 52px;
  height: 52px;
  border-radius: 9999px;
  color: white;
  font-size: 13px;
  font-weight: 700;
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.12);
}
</style>
