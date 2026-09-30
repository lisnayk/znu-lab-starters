const API_URL = 'https://dummyjson.com/products'

export const PAGE_SIZE = 12
export const API_DELAY = 1500

export function createInitialProductsUrl() {
  const params = new URLSearchParams({
    limit: String(PAGE_SIZE),
    delay: String(API_DELAY),
  })

  return `${API_URL}?${params}`
}
