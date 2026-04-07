import { computed, ref } from 'vue';

export type InputMode =
  | 'normal'
  | 'wide_research'
  | 'slides'
  | 'website'
  | 'design'
  | 'spreadsheet'
  | 'video'
  | 'audio'
  | 'chat'
  | 'schedule'
  | 'visualization'
  | 'develop_apps'
  | 'playbook';
export type DesignModel = 'Forge Image v1' | 'Forge Image v2 Pro';

export const slidesTemplates = [
  'Minimal',
  'Dark',
  'Corporate',
  'Creative',
  'Tech',
  'Elegant',
  'Bold',
  'Pastel',
] as const;

export const websiteCategories = [
  'Landing Page',
  'Dashboard',
  'Portfolio',
  'Corporate',
  'SaaS',
  'E-commerce',
  'Blog',
  'Docs',
] as const;

export function useInputMode(initialMode: InputMode = 'normal') {
  const inputMode = ref<InputMode>(initialMode);
  const designModel = ref<DesignModel>('Forge Image v1');
  const slidesTemplate = ref<(typeof slidesTemplates)[number]>('Minimal');
  const websiteCategory = ref<(typeof websiteCategories)[number]>('SaaS');
  const wideResearchFlag = computed(() => inputMode.value === 'wide_research');

  const placeholder = computed(() => {
    if (inputMode.value === 'wide_research') return 'Conduct deep research on...';
    if (inputMode.value === 'slides') return 'Create a presentation about...';
    if (inputMode.value === 'website') return 'Describe the website you want to build';
    if (inputMode.value === 'design') return 'Describe the image you want to create';
    if (inputMode.value === 'spreadsheet') return 'Upload a spreadsheet to analyze or start one from scratch';
    if (inputMode.value === 'video') return 'Describe the video you want to create';
    if (inputMode.value === 'audio') return 'Describe the audio you want to create';
    if (inputMode.value === 'chat') return 'Ask anything';
    if (inputMode.value === 'schedule') return "Describe a task to run on a schedule, e.g. 'send a daily market briefing to my email every morning at 8am'";
    if (inputMode.value === 'visualization') return 'Describe the data visualization you want';
    if (inputMode.value === 'develop_apps') return 'Describe the app you want to build';
    if (inputMode.value === 'playbook') return 'Describe a workflow or playbook to automate';
    return 'Assign a task to Forge...';
  });

  const activateMode = (mode: InputMode) => {
    inputMode.value = mode;
  };

  const clearMode = () => {
    inputMode.value = 'normal';
  };

  const buildModeConfig = () => ({
    designModel: designModel.value,
    slidesTemplate: slidesTemplate.value,
    websiteCategory: websiteCategory.value,
  });

  return {
    inputMode,
    designModel,
    slidesTemplate,
    websiteCategory,
    wideResearchFlag,
    placeholder,
    activateMode,
    clearMode,
    buildModeConfig,
  };
}
