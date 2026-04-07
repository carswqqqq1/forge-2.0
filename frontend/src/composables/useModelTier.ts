import { computed, ref, watch } from 'vue';

export type ForgeModelTier = 'lite' | 'regular' | 'max';

const STORAGE_KEY = 'forge-model-tier';

const getInitialTier = (): ForgeModelTier => {
  const saved = localStorage.getItem(STORAGE_KEY) as ForgeModelTier | null;
  if (saved === 'lite' || saved === 'regular' || saved === 'max') {
    return saved;
  }
  return 'regular';
};

const selectedTier = ref<ForgeModelTier>(getInitialTier());

watch(selectedTier, (value) => {
  localStorage.setItem(STORAGE_KEY, value);
});

const tierMeta = {
  max: {
    key: 'max' as const,
    title: 'Forge Max',
    description: 'Most powerful',
    creditLabel: '5 credits/step',
    shortLabel: 'Forge Max',
  },
  regular: {
    key: 'regular' as const,
    title: 'Forge',
    description: 'Balanced',
    creditLabel: '2 credits/step',
    shortLabel: 'Forge',
  },
  lite: {
    key: 'lite' as const,
    title: 'Forge Lite',
    description: 'Fast & efficient',
    creditLabel: '1 credit/step',
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
