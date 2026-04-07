import { computed, ref, watch } from 'vue';

export type ForgeModelTier = 'lite' | 'regular' | 'max';

const STORAGE_KEY = 'forge-model-tier';

const getInitialTier = (): ForgeModelTier => {
  const saved = localStorage.getItem(STORAGE_KEY) as ForgeModelTier | null;
  if (saved === 'lite' || saved === 'regular' || saved === 'max') {
    return saved;
  }
  return 'lite';
};

const selectedTier = ref<ForgeModelTier>(getInitialTier());

watch(selectedTier, (value) => {
  localStorage.setItem(STORAGE_KEY, value);
});

const tierMeta = {
  max: {
    key: 'max' as const,
    title: 'Forge Max',
    description: 'High-performance model for complex tasks.',
    shortLabel: 'Forge Max',
  },
  regular: {
    key: 'regular' as const,
    title: 'Forge Regular',
    description: 'Versatile agent capable of most tasks.',
    shortLabel: 'Forge Regular',
  },
  lite: {
    key: 'lite' as const,
    title: 'Forge Lite',
    description: 'A lightweight agent for everyday tasks.',
    shortLabel: 'Forge Lite',
  },
};

export function useModelTier() {
  const currentTier = computed(() => selectedTier.value);
  const currentTierMeta = computed(() => tierMeta[selectedTier.value]);

  const setModelTier = (tier: ForgeModelTier) => {
    selectedTier.value = tier;
  };

  return {
    currentTier,
    currentTierMeta,
    modelOptions: [tierMeta.max, tierMeta.regular, tierMeta.lite],
    setModelTier,
  };
}
