<template>
  <!--
    Розмітка перенесена з прикладу «Tabs with Automatic Activation»
    (WAI-ARIA Authoring Practices Guide). Склад елементів, ролі, зв'язки
    id → aria-controls і aria-labelledby, aria-selected та tabindex збережено;
    змінено лише класи — їх названо за BEM — і текст вкладок.
    Логіки тут немає: активною показано першу вкладку, решту панелей приховано
    модифікатором. Перемикання реалізується в компонентах Tabs і Tab.
  -->
  <div class="tabs tabs--underline">
    <h3 id="tablist-1" class="tabs__title">Компонент вкладок у Vue</h3>

    <div role="tablist" aria-labelledby="tablist-1" class="tabs__list">
      <button id="tab-1"
              type="button"
              role="tab"
              aria-selected="true"
              aria-controls="tabpanel-1"
              class="tabs__tab tabs__tab--active">
        <span class="tabs__label">Огляд</span>
      </button>
      <button id="tab-2"
              type="button"
              role="tab"
              aria-selected="false"
              aria-controls="tabpanel-2"
              tabindex="-1"
              class="tabs__tab">
        <span class="tabs__label">Вимоги</span>
      </button>
      <button id="tab-3"
              type="button"
              role="tab"
              aria-selected="false"
              aria-controls="tabpanel-3"
              tabindex="-1"
              class="tabs__tab">
        <span class="tabs__label">Середовище</span>
      </button>
    </div>

    <div id="tabpanel-1"
         role="tabpanel"
         tabindex="0"
         aria-labelledby="tab-1"
         class="tabs__panel">
      <p class="tabs__text">
        Матеріал показує складений компонент вкладок, частини якого обмінюються
        локальним контекстом. Тема — слоти та provide/inject, тривалість
        заняття — чотири години.
      </p>
      <p class="tabs__text">
        У робочій версії панель має власний локальний стан — текстове поле,
        прапорець і лічильник. Їхні значення зберігаються під час переходу на
        іншу вкладку та повернення назад.
      </p>
    </div>

    <div id="tabpanel-2"
         role="tabpanel"
         tabindex="0"
         aria-labelledby="tab-2"
         class="tabs__panel tabs__panel--hidden">
      <p class="tabs__text">
        Потрібні Node.js 24 LTS, npm, Git і редактор коду, а також власний
        компонент ModalDialog, перенесений з лабораторної роботи 3.
      </p>
      <p class="tabs__text">
        Оформлення спирається на Tailwind CSS 3.4.17 із PostCSS 8 та
        Autoprefixer 10; Sass встановлюється як devDependency, бо стилі
        компонентів пишуться мовою SCSS.
      </p>
    </div>

    <div id="tabpanel-3"
         role="tabpanel"
         tabindex="0"
         aria-labelledby="tab-3"
         class="tabs__panel tabs__panel--hidden">
      <p class="tabs__text">
        Проєкт збирається Vite. Сервер розробки запускається командою
        npm run dev -- --port 5173 --strictPort, готова збірка — командою
        npm run build.
      </p>
      <p class="tabs__text">
        Вигляд перевіряється в браузері з увімкненими DevTools на ширинах
        360×800, 768×1024, 1440×900 і 844×390.
      </p>
    </div>
  </div>
</template>

<style scoped lang="scss">
// Кольори й шрифти беруться з tailwind.config.js, куди їх перенесено
// з theme/tokens.yaml. Значень кольору в цьому файлі немає.
.tabs {
  $self: &;

  @apply overflow-hidden rounded-xl border border-edge bg-paper;

  &__title {
    @apply border-b border-edge px-4 py-3 font-display text-base font-bold text-ink;
  }

  // Смуга кнопок не прокручується: за браком місця вкладки переносяться
  // на наступний рядок, тому жодна з них не лишається поза екраном.
  &__list {
    @apply flex flex-wrap gap-x-1 px-2;
  }

  &__tab {
    @apply flex min-h-11 items-center px-4 py-2 text-sm font-semibold text-muted;
    @apply transition-colors hover:text-ink;
    @apply focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ink;
  }

  &__label {
    @apply whitespace-nowrap;
  }

  &__panel {
    @apply px-4 py-4;
    @apply focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-ink;

    &--hidden {
      @apply hidden;
    }
  }

  &__text {
    @apply text-sm leading-relaxed text-ink;

    & + & {
      @apply mt-3;
    }
  }

  // Варіант оформлення смуги. Модифікатор перевизначає вигляд елементів
  // блока, а назви класів не складаються з частин у шаблоні.
  &--underline {
    #{$self}__list {
      @apply border-b-2 border-edge;
    }

    #{$self}__tab {
      @apply -mb-0.5 border-b-2 border-transparent;
    }

    #{$self}__tab--active {
      @apply border-accent text-ink;
    }
  }
}
</style>
