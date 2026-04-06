<template>
  <svg :width="width" :height="height" viewBox="0 0 90 40" fill="none" xmlns="http://www.w3.org/2000/svg">
    <text x="0" y="28" fill="var(--logo-color)" font-size="22" font-weight="700" font-family="ui-serif, Georgia, serif">
      Forge
    </text>
  </svg>
</template>

<script setup lang="ts">
defineProps({
  width: {
    type: [String, Number],
    default: 120
  },
  height: {
    type: [String, Number],
    default: 30
  }
})
</script>
