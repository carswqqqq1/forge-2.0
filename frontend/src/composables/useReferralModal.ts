import { ref } from 'vue';

const isReferralModalOpen = ref(false);

export function useReferralModal() {
  const openReferralModal = () => {
    isReferralModalOpen.value = true;
  };

  const closeReferralModal = () => {
    isReferralModalOpen.value = false;
  };

  return {
    isReferralModalOpen,
    openReferralModal,
    closeReferralModal,
  };
}
