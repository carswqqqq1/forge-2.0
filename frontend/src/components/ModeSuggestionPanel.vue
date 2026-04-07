<template>
  <div v-if="mode !== 'normal'" class="mt-4 flex flex-col gap-4">
    <div v-if="mode === 'wide_research'" class="flex flex-wrap gap-2">
      <button v-for="item in wideResearchSuggestions" :key="item" class="suggestion-chip" @click="$emit('apply-prompt', item)">
        {{ item }}
      </button>
    </div>

    <template v-else-if="mode === 'slides'">
      <div class="flex flex-wrap gap-2">
        <button v-for="item in slidesSuggestions" :key="item" class="suggestion-chip" @click="$emit('apply-prompt', item)">
          {{ item }}
        </button>
      </div>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
        <button
          v-for="template in slideTemplates"
          :key="template"
          class="template-card"
          :class="selectedSlidesTemplate === template ? 'template-card--active' : ''"
          @click="$emit('update:slidesTemplate', template)">
          <div class="template-card__preview" :style="gradientFor(template)"></div>
          <div class="template-card__label">{{ template }}</div>
        </button>
      </div>
    </template>

    <template v-else-if="mode === 'website'">
      <div class="flex flex-wrap gap-2">
        <button
          v-for="category in websiteCategories"
          :key="category"
          class="suggestion-chip"
          :class="selectedWebsiteCategory === category ? 'suggestion-chip--active' : ''"
          @click="$emit('update:websiteCategory', category)">
          {{ category }}
        </button>
      </div>
      <div class="rounded-[20px] border border-[var(--border-main)] bg-white p-4">
        <div class="text-[13px] font-medium uppercase tracking-[0.08em] text-[var(--text-tertiary)]">Powerful built-in integrations</div>
        <div class="mt-3 flex flex-wrap gap-2">
          <span v-for="tag in websiteIntegrations" :key="tag" class="integration-tag">{{ tag }}</span>
        </div>
        <div class="mt-4 flex flex-wrap gap-2">
          <button class="secondary-link" @click="$emit('apply-prompt', 'Use this site as a visual reference: ')">Add website reference</button>
          <button class="secondary-link" @click="$emit('apply-prompt', 'Import this Figma design into a website build: ')">Import from Figma</button>
        </div>
      </div>
    </template>

    <template v-else-if="mode === 'design'">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
        <button v-for="card in designSuggestions" :key="card.title" class="design-card" @click="$emit('apply-prompt', card.prompt)">
          <div class="design-card__thumb" :style="card.gradient"></div>
          <div class="mt-3 text-sm font-medium text-[var(--text-primary)]">{{ card.title }}</div>
          <div class="mt-1 text-[12px] text-[var(--text-secondary)]">{{ card.prompt }}</div>
        </button>
      </div>
    </template>

    <template v-else-if="mode === 'spreadsheet'">
      <div class="flex flex-wrap gap-2">
        <button v-for="item in spreadsheetSuggestions" :key="item" class="suggestion-chip" @click="$emit('apply-prompt', item)">
          {{ item }}
        </button>
      </div>
    </template>

    <template v-else-if="mode === 'video'">
      <div class="flex flex-wrap gap-2">
        <button v-for="item in videoSuggestions" :key="item" class="suggestion-chip" @click="$emit('apply-prompt', item)">
          {{ item }}
        </button>
      </div>
    </template>

    <template v-else-if="mode === 'audio'">
      <div class="flex flex-wrap gap-2">
        <button v-for="item in audioSuggestions" :key="item" class="suggestion-chip" @click="$emit('apply-prompt', item)">
          {{ item }}
        </button>
      </div>
    </template>

    <template v-else-if="mode === 'schedule'">
      <div class="flex justify-end">
        <button class="outlined-action" @click="$emit('apply-prompt', 'Send me a daily market briefing every morning')">
          + New schedule
        </button>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-2">
        <button v-for="item in scheduleSuggestions" :key="item" class="suggestion-chip h-full text-left" @click="$emit('apply-prompt', item)">
          {{ item }}
        </button>
      </div>
    </template>

    <template v-else-if="mode === 'visualization'">
      <div class="flex flex-wrap gap-2">
        <button v-for="item in visualizationSuggestions" :key="item" class="suggestion-chip" @click="$emit('apply-prompt', item)">
          {{ item }}
        </button>
      </div>
    </template>

    <template v-else-if="mode === 'develop_apps'">
      <div class="flex flex-wrap gap-2">
        <button v-for="item in developAppsSuggestions" :key="item" class="suggestion-chip" @click="$emit('apply-prompt', item)">
          {{ item }}
        </button>
      </div>
    </template>

    <template v-else-if="mode === 'playbook'">
      <div class="flex flex-wrap gap-2">
        <button v-for="item in playbookSuggestions" :key="item" class="suggestion-chip" @click="$emit('apply-prompt', item)">
          {{ item }}
        </button>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import type { InputMode } from '../composables/useInputMode';

defineProps<{
  mode: InputMode;
  selectedSlidesTemplate?: string;
  selectedWebsiteCategory?: string;
}>();

defineEmits<{
  (e: 'apply-prompt', prompt: string): void;
  (e: 'update:slidesTemplate', template: string): void;
  (e: 'update:websiteCategory', category: string): void;
}>();

const wideResearchSuggestions = [
  'Conduct comprehensive market sizing analysis',
  'Conduct deep competitor benchmarking study',
  'Research emerging technology landscape',
  'Conduct investment due diligence research',
  'Research customer personas and journey maps',
];

const slidesSuggestions = [
  'Create a board-ready pitch deck about Forge',
  'Build a product launch deck for a new SaaS',
  'Turn this research into a client presentation',
  'Create an investor update presentation',
];

const slideTemplates = ['Minimal', 'Dark', 'Corporate', 'Creative', 'Tech', 'Elegant', 'Bold', 'Pastel'];
const websiteCategories = ['Landing Page', 'Dashboard', 'Portfolio', 'Corporate', 'SaaS', 'E-commerce', 'Blog', 'Docs'];
const websiteIntegrations = ['Auth', 'Database', 'Payments', 'AI/LLM', 'Maps', 'Email', 'Storage', 'API'];

const designSuggestions = [
  { title: 'Hero Illustration', prompt: 'Create a sleek AI workspace hero illustration', gradient: 'background: linear-gradient(135deg, #111827, #4b5563);' },
  { title: 'App Mockup', prompt: 'Design a premium SaaS dashboard mockup in black and white', gradient: 'background: linear-gradient(135deg, #f8fafc, #d1d5db);' },
  { title: 'Brand Poster', prompt: 'Design a bold brand poster for Forge with editorial typography', gradient: 'background: linear-gradient(135deg, #111111, #ef4444);' },
];

const spreadsheetSuggestions = [
  'Create a sales tracker with monthly revenue, expenses, profit columns',
  'Analyze this CSV and visualize trends as charts',
  'Build a budget spreadsheet with categories and totals',
  'Convert this data into a pivot table',
  'Generate a project timeline with Gantt-style formatting',
];

const videoSuggestions = [
  'Create a 60-second product demo video script with scene-by-scene breakdown',
  'Generate a YouTube intro sequence concept with timestamps',
  'Write a storyboard for a 30-second ad spot',
  'Create a video essay outline with talking points',
  'Generate B-roll shot list for a travel vlog',
];

const audioSuggestions = [
  'Write lyrics for an upbeat pop song about entrepreneurship',
  'Create a podcast intro script with host intro and topic overview',
  'Generate a 3-minute meditation script with calm narration',
  'Write a jingle for a marketing campaign',
  'Create a voiceover script for a product explainer',
];

const scheduleSuggestions = [
  'Send me a daily market briefing every morning',
  'Monitor competitor websites for changes weekly',
  'Generate weekly performance reports from my data',
  'Send daily social media post ideas at 9am',
  'Run a weekly SEO audit on my website',
  'Send a Monday morning task summary email',
];

const visualizationSuggestions = [
  'Create an interactive bar chart of monthly sales data',
  'Visualize user growth trends over the last 12 months',
  'Build a dashboard showing KPIs with color-coded metrics',
  'Create a geographic heatmap of customer locations',
  'Generate a funnel chart for conversion rates',
];

const developAppsSuggestions = [
  'Build a React dashboard with login, sidebar, and data tables',
  'Create a REST API with authentication and CRUD endpoints',
  'Build a Chrome extension that summarizes web pages',
  'Create a mobile-responsive landing page with animations',
  'Build a CLI tool that processes CSV files',
];

const playbookSuggestions = [
  'Create an onboarding playbook for new sales team members',
  'Build a content creation workflow from idea to published post',
  'Create a customer support escalation playbook',
  'Build a lead qualification and follow-up automation',
  'Create a product launch checklist and execution playbook',
];

const gradientFor = (template: string) => {
  const gradients: Record<string, string> = {
    Minimal: 'background: linear-gradient(135deg, #ffffff, #e5e7eb);',
    Dark: 'background: linear-gradient(135deg, #111827, #374151);',
    Corporate: 'background: linear-gradient(135deg, #dbeafe, #93c5fd);',
    Creative: 'background: linear-gradient(135deg, #f97316, #fb7185);',
    Tech: 'background: linear-gradient(135deg, #0f172a, #38bdf8);',
    Elegant: 'background: linear-gradient(135deg, #f5f5f4, #d6d3d1);',
    Bold: 'background: linear-gradient(135deg, #111827, #f59e0b);',
    Pastel: 'background: linear-gradient(135deg, #fce7f3, #ddd6fe);',
  };
  return gradients[template] || gradients.Minimal;
};
</script>

<style scoped>
.suggestion-chip,
.integration-tag,
.secondary-link {
  border-radius: 9999px;
  border: 1px solid var(--border-main);
  background: var(--background-white-main);
  font-size: 13px;
}

.suggestion-chip {
  padding: 8px 14px;
  color: var(--text-secondary);
}

.suggestion-chip--active {
  background: #111827;
  color: white;
  border-color: #111827;
}

.integration-tag {
  padding: 8px 12px;
  color: var(--text-secondary);
}

.secondary-link {
  padding: 8px 14px;
  color: var(--text-primary);
}

.outlined-action {
  border-radius: 9999px;
  border: 1px solid var(--border-main);
  background: white;
  padding: 8px 14px;
  font-size: 13px;
  color: var(--text-primary);
}

.template-card,
.design-card {
  border-radius: 18px;
  border: 1px solid var(--border-main);
  background: white;
  padding: 12px;
  text-align: left;
}

.template-card--active {
  border-color: #111827;
  box-shadow: 0 0 0 1px #111827 inset;
}

.template-card__preview,
.design-card__thumb {
  height: 84px;
  border-radius: 14px;
}

.template-card__label {
  margin-top: 10px;
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
}
</style>
