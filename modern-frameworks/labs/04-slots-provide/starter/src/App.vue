<script setup>
import TabsDesign from '@/components/tabs/TabsDesign.vue'
</script>

<template>
  <div class="page">
    <header class="page__header">
      <h1 class="page__title">Оформлення вкладок</h1>
      <p class="page__lead">
        Зразок вигляду складеного компонента вкладок лабораторної роботи 4.
        Розмітка відповідає прикладу «Tabs with Automatic Activation» зі
        збірника WAI-ARIA Authoring Practices, оформлення задано класами BEM
        і утилітами Tailwind CSS.
      </p>
    </header>

    <main class="page__content">
      <TabsDesign/>
    </main>
  </div>
</template>

<style scoped lang="scss">
.page {
  @apply min-h-screen bg-surface px-4 py-8;

  &__header {
    @apply mx-auto max-w-3xl;
  }

  &__title {
    @apply font-display text-2xl font-bold text-ink;
  }

  &__lead {
    @apply mt-3 text-sm leading-relaxed text-muted;
  }

  &__content {
    @apply mx-auto mt-6 max-w-3xl;
  }
}
</style>
