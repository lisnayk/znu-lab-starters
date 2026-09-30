<script setup>
import { onMounted, ref } from 'vue'
import {
  API_DELAY,
  createInitialProductsUrl,
} from './api/products.js'

const query = ref('')
const products = ref([])
const total = ref(0)
const isLoading = ref(false)
const error = ref(null)

const priceFormatter = new Intl.NumberFormat('uk-UA', {
  style: 'currency',
  currency: 'USD',
  maximumFractionDigits: 2,
})

async function loadInitialProducts() {
  isLoading.value = true
  error.value = null

  try {
    const response = await fetch(createInitialProductsUrl())

    if (!response.ok)
      throw new Error(`HTTP ${response.status}`)

    const page = await response.json()
    products.value = page.products
    total.value = page.total
  } catch (cause) {
    error.value = cause
  } finally {
    isLoading.value = false
  }
}

function submitSearch() {
  // TODO: студент реалізує реактивний пошук із debounce та abort.
}

onMounted(loadInitialProducts)
</script>

<template>
  <main class="storefront">
    <header class="storefront__masthead">
      <a class="storefront__brand" href="#" aria-label="Forma, на початок">
        FORMA<span class="storefront__brand-mark">®</span>
      </a>
      <p class="storefront__edition">Лабораторна / 05</p>
      <p class="storefront__note">Каталог і composables</p>
    </header>

    <section class="storefront__hero">
      <div class="storefront__intro">
        <p class="storefront__eyebrow">Заготовка інтерфейсу</p>
        <h1 class="storefront__title">
          Речі з ясною
          <em class="storefront__title-accent">формою</em>
        </h1>
      </div>

      <form class="search-panel" role="search" @submit.prevent="submitSearch">
        <label class="search-panel__label" for="product-search">
          Пошук у каталозі
        </label>
        <div class="search-panel__control">
          <svg
            class="search-panel__icon"
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <circle cx="10.5" cy="10.5" r="6.5" />
            <path d="m15.5 15.5 5 5" />
          </svg>
          <input
            id="product-search"
            v-model="query"
            class="search-panel__input"
            type="search"
            placeholder="Форма поки не виконує пошук"
            autocomplete="off"
          />
          <span class="search-panel__hint">TODO</span>
        </div>
        <p class="search-panel__status" aria-live="polite">
          <span
            class="search-panel__status-dot"
            :class="{ 'search-panel__status-dot--active': isLoading }"
          ></span>
          <span v-if="isLoading">Завантажуємо початкові товари…</span>
          <span v-else-if="error">Не вдалося отримати товари</span>
          <span v-else>Показано {{ products.length }} із {{ total }} товарів</span>
          <span class="search-panel__delay">API +{{ API_DELAY }} мс</span>
        </p>
      </form>
    </section>

    <section class="catalog" aria-labelledby="catalog-title">
      <div class="catalog__heading">
        <h2 id="catalog-title" class="catalog__title">Початкова добірка</h2>
        <span class="catalog__count">{{ products.length.toString().padStart(2, '0') }}</span>
      </div>

      <div v-if="products.length" class="catalog__grid">
        <!-- TODO: винести одну картку в ProductCard.vue, а список — у ProductCatalog.vue. -->
        <article
          v-for="product in products"
          :key="product.id"
          class="product-card"
        >
          <div class="product-card__visual">
            <span
              v-if="product.discountPercentage >= 10"
              class="product-card__discount"
            >
              −{{ Math.round(product.discountPercentage) }}%
            </span>
            <img
              class="product-card__image"
              :src="product.thumbnail"
              :alt="product.title"
              loading="lazy"
              width="420"
              height="320"
            />
          </div>

          <div class="product-card__body">
            <div class="product-card__meta">
              <span class="product-card__category">{{ product.category }}</span>
              <span class="product-card__rating">
                {{ product.rating.toFixed(1) }} / 5
              </span>
            </div>

            <h2 class="product-card__title">{{ product.title }}</h2>
            <p class="product-card__description">{{ product.description }}</p>

            <div class="product-card__footer">
              <strong class="product-card__price">
                {{ priceFormatter.format(product.price) }}
              </strong>
              <span class="product-card__stock">
                {{ product.stock > 0 ? `У наявності · ${product.stock}` : 'Немає в наявності' }}
              </span>
            </div>
          </div>
        </article>
      </div>

      <div v-if="products.length" class="catalog__load-more">
        <span class="catalog__load-progress">{{ products.length }} / {{ total }}</span>
        <div class="catalog__load-copy">
          <strong class="catalog__load-title">Автозавантаження не підключено</strong>
          <span class="catalog__load-text">
            Нижній маркер не спостерігається і не змінює сторінку
          </span>
        </div>
      </div>

      <div v-else-if="isLoading" class="catalog__skeletons" aria-hidden="true">
        <div v-for="item in 6" :key="item" class="catalog__skeleton"></div>
      </div>

      <div v-else-if="error" class="catalog__message catalog__message--error">
        <p class="catalog__message-index">ERR / API</p>
        <h2 class="catalog__message-title">Каталог тимчасово недоступний</h2>
        <p class="catalog__message-text">{{ error.message }}</p>
        <button class="catalog__retry" type="button" @click="loadInitialProducts">
          Повторити запит
        </button>
      </div>
    </section>

    <footer class="storefront__footer">
      <p>Студент: Прізвище Ім’я · група</p>
      <a href="https://dummyjson.com/docs/products" target="_blank" rel="noreferrer">
        Дані: DummyJSON
      </a>
    </footer>
  </main>
</template>
