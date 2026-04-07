import { computed, ref } from 'vue';

export type InputMode = 'normal' | 'wide_research' | 'slides' | 'website' | 'design';
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
