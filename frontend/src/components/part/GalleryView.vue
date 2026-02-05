<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'

type MediaType = 'image' | 'video'

type MediaItem = {
  name: string
  url: string
  type: MediaType
}

const { t } = useI18n()

const mediaItems = ref<MediaItem[]>([])
const isLoading = ref(true)
const hasError = ref(false)
const activeFilter = ref<'all' | 'image' | 'video'>('all')
const selectedItem = ref<MediaItem | null>(null)
const currentPage = ref(1)
const pageSize = 12

const imageExtensions = new Set(['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp', 'avif'])
const videoExtensions = new Set(['mp4', 'webm', 'ogg', 'mov', 'm4v'])

const getMediaType = (fileName: string): MediaType | null => {
  const ext = fileName.split('.').pop()?.toLowerCase() ?? ''
  if (imageExtensions.has(ext)) return 'image'
  if (videoExtensions.has(ext)) return 'video'
  return null
}

const buildUrl = (fileName: string) => {
  if (/^https?:\/\//i.test(fileName)) return fileName
  if (fileName.startsWith('/')) return fileName
  return `/photos/${fileName}`
}

const getDevFallbackItems = (): MediaItem[] => {
  if (!import.meta.env.DEV) return []
  const modules = import.meta.glob(
    '../../../../photos/*.{jpg,jpeg,png,gif,webp,bmp,avif,mp4,webm,ogg,mov,m4v}',
    { eager: true, query: '?url', import: 'default' },
  ) as Record<string, string>
  const items = Object.entries(modules)
    .map(([filePath, url]) => {
      const name = filePath.split('/').pop() ?? filePath
      const type = getMediaType(name)
      if (!type) return null
      return {
        name,
        url,
        type,
      }
    })
    .filter((item): item is MediaItem => item !== null)
  return items.sort((a, b) =>
    a.name.localeCompare(b.name, undefined, { numeric: true, sensitivity: 'base' }),
  )
}

const filteredItems = computed(() => {
  if (activeFilter.value === 'all') return mediaItems.value
  return mediaItems.value.filter((item) => item.type === activeFilter.value)
})

const totalPages = computed(() => Math.ceil(filteredItems.value.length / pageSize))

const pagedItems = computed(() => {
  if (totalPages.value === 0) return []
  const start = (currentPage.value - 1) * pageSize
  return filteredItems.value.slice(start, start + pageSize)
})

const pageNumbers = computed(() =>
  Array.from({ length: totalPages.value }, (_, index) => index + 1),
)

const applyPage = (page: number) => {
  if (totalPages.value === 0) return
  if (page < 1 || page > totalPages.value) return
  currentPage.value = page
}

const openLightbox = (item: MediaItem) => {
  selectedItem.value = item
}

const closeLightbox = () => {
  selectedItem.value = null
}

const handleKeydown = (event: KeyboardEvent) => {
  if (event.key !== 'Escape') return
  closeLightbox()
}

watch(activeFilter, () => {
  currentPage.value = 1
})

watch(filteredItems, () => {
  if (totalPages.value === 0) {
    currentPage.value = 1
    return
  }
  if (currentPage.value > totalPages.value) {
    currentPage.value = totalPages.value
  }
})

watch(selectedItem, (next) => {
  if (next) {
    document.addEventListener('keydown', handleKeydown)
    document.body.style.overflow = 'hidden'
    return
  }
  document.removeEventListener('keydown', handleKeydown)
  document.body.style.overflow = ''
})

const fetchMedia = async () => {
  isLoading.value = true
  hasError.value = false
  try {
    const response = await fetch('/api/gallery')
    if (!response.ok) throw new Error('Failed to fetch photos')
    const data = await response.json()
    const rawList = Array.isArray(data) ? data : Array.isArray(data?.files) ? data.files : []
    const files = rawList.filter((item): item is string => typeof item === 'string')
    const sortedFiles = files.sort((a, b) =>
      a.localeCompare(b, undefined, { numeric: true, sensitivity: 'base' }),
    )
    const mapped = sortedFiles
      .map((fileName) => {
        const type = getMediaType(fileName)
        if (!type) return null
        return {
          name: fileName,
          url: buildUrl(fileName),
          type,
        }
      })
      .filter((item): item is MediaItem => item !== null)
    mediaItems.value = mapped
  } catch (error) {
    const fallbackItems = getDevFallbackItems()
    if (fallbackItems.length > 0) {
      hasError.value = false
      mediaItems.value = fallbackItems
    } else {
      hasError.value = true
      mediaItems.value = []
    }
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  fetchMedia()
})

onBeforeUnmount(() => {
  document.removeEventListener('keydown', handleKeydown)
  document.body.style.overflow = ''
})
</script>
<template>
  <div class="space-y-6">
    <div class="space-y-1">
      <div class="section-title">{{ t('gallery.title') }}</div>
      <div class="flex flex-wrap gap-3 pb-3 pt-7">
        <button
          type="button"
          class="rounded-xl font-semibold bg-white px-5 py-2 shadow-[3px_3px_10px_rgba(0,0,0,0.12)] transition"
          :class="
            activeFilter === 'all'
              ? 'border-[--mdark] border text-[--mdark] '
              : 'text-black/70 hover:border-black/20'
          "
          :aria-pressed="activeFilter === 'all'"
          @click="activeFilter = 'all'"
        >
          {{ t('gallery.filters.all') }}
        </button>
        <button
          type="button"
          class="rounded-xl font-semibold bg-white px-5 py-2 shadow-[3px_3px_10px_rgba(0,0,0,0.12)] transition"
          :class="
            activeFilter === 'image'
              ? 'border-[--mdark] border text-[--mdark] '
              : 'text-black/70 hover:border-black/20'
          "
          :aria-pressed="activeFilter === 'image'"
          @click="activeFilter = 'image'"
        >
          {{ t('gallery.filters.photo') }}
        </button>
        <button
          type="button"
          class="rounded-xl font-semibold bg-white px-5 py-2 shadow-[3px_3px_10px_rgba(0,0,0,0.12)] transition"
          :class="
            activeFilter === 'video'
              ? 'border-[--mdark] border text-[--mdark] '
              : 'text-black/70 hover:border-black/20'
          "
          :aria-pressed="activeFilter === 'video'"
          @click="activeFilter = 'video'"
        >
          {{ t('gallery.filters.video') }}
        </button>
      </div>
      <p class="text-[--mblue]">{{ t('gallery.description') }}</p>
    </div>

    <div
      v-if="isLoading"
      class="rounded-2xl border border-dashed border-black/10 py-16 text-center"
    >
      <p class="text-black/50">{{ t('gallery.loading') }}</p>
    </div>
    <div
      v-else-if="hasError"
      class="rounded-2xl border border-dashed border-black/10 py-16 text-center"
    >
      <p class="text-black/50">{{ t('gallery.error') }}</p>
    </div>
    <div
      v-else-if="pagedItems.length === 0"
      class="rounded-2xl border border-dashed border-black/10 py-16 text-center"
    >
      <p class="text-black/50">{{ t('gallery.empty') }}</p>
    </div>

    <div v-else class="columns-2 gap-5 sm:columns-3">
      <button
        v-for="item in pagedItems"
        :key="item.name"
        type="button"
        class="mb-5 inline-block w-full break-inside-avoid overflow-hidden rounded-2xl border border-black/10 bg-white shadow-[0_10px_20px_rgba(0,0,0,0.12)] transition hover:-translate-y-1 hover:shadow-[0_16px_30px_rgba(0,0,0,0.16)]"
        @click="openLightbox(item)"
      >
        <img
          v-if="item.type === 'image'"
          :src="item.url"
          :alt="item.name"
          class="h-auto w-full object-cover"
          loading="lazy"
        />
        <video
          v-else
          :src="item.url"
          class="h-auto w-full object-cover"
          controls
          preload="metadata"
        ></video>
      </button>
    </div>

    <div v-if="totalPages > 1" class="flex items-center justify-center gap-2 pt-2">
      <button
        type="button"
        class="flex h-9 w-9 items-center justify-center rounded-lg border border-[--mblue] text-[--mblue] transition hover:border-[--mdark] hover:text-[--mdark]"
        :disabled="currentPage === 1"
        :class="currentPage === 1 ? 'opacity-40' : ''"
        @click="applyPage(1)"
      >
        <span class="material-symbols-rounded text-base">keyboard_double_arrow_left</span>
      </button>
      <button
        type="button"
        class="flex h-9 w-9 items-center justify-center rounded-lg border border-[--mblue] text-[--mblue] transition hover:border-[--mdark] hover:text-[--mdark]"
        :disabled="currentPage === 1"
        :class="currentPage === 1 ? 'opacity-40' : ''"
        @click="applyPage(currentPage - 1)"
      >
        <span class="material-symbols-rounded text-base">chevron_left</span>
      </button>
      <button
        v-for="page in pageNumbers"
        :key="`page-${page}`"
        type="button"
        class="flex h-9 w-9 items-center justify-center rounded-lg border transition"
        :class="
          page === currentPage
            ? 'border-[--mdark] text-[--mdark]'
            : 'border-[--mblue] text-[--mblue] hover:border-[--mdark] hover:text-[--mdark]'
        "
        @click="applyPage(page)"
      >
        {{ page }}
      </button>
      <button
        type="button"
        class="flex h-9 w-9 items-center justify-center rounded-lg border border-[--mblue] text-[--mblue] transition hover:border-[--mdark] hover:text-[--mdark]"
        :disabled="currentPage === totalPages"
        :class="currentPage === totalPages ? 'opacity-40' : ''"
        @click="applyPage(currentPage + 1)"
      >
        <span class="material-symbols-rounded text-base">chevron_right</span>
      </button>
      <button
        type="button"
        class="flex h-9 w-9 items-center justify-center rounded-lg border border-[--mblue] text-[--mblue] transition hover:border-[--mdark] hover:text-[--mdark]"
        :disabled="currentPage === totalPages"
        :class="currentPage === totalPages ? 'opacity-40' : ''"
        @click="applyPage(totalPages)"
      >
        <span class="material-symbols-rounded text-base">keyboard_double_arrow_right</span>
      </button>
    </div>
  </div>
  <teleport to="body">
    <div
      v-if="selectedItem"
      class="fixed inset-0 z-[120] flex items-center justify-center px-4 py-10"
      role="dialog"
      aria-modal="true"
      :aria-label="t('gallery.lightboxLabel')"
    >
      <button type="button" class="absolute inset-0 bg-black/60" @click="closeLightbox"></button>
      <div
        class="relative w-full max-w-4xl overflow-hidden rounded-2xl bg-white shadow-[0_20px_60px_rgba(0,0,0,0.28)]"
      >
        <button
          type="button"
          class="absolute right-4 top-4 rounded-full border border-black/10 bg-white px-4 py-2 text-xs font-semibold text-black/70 transition hover:border-black/20 hover:text-black"
          @click="closeLightbox"
        >
          {{ t('gallery.close') }}
        </button>
        <div class="max-h-[80vh] overflow-auto p-4">
          <img
            v-if="selectedItem?.type === 'image'"
            :src="selectedItem.url"
            :alt="selectedItem.name"
            class="h-auto w-full rounded-xl object-contain"
          />
          <video
            v-else
            :src="selectedItem.url"
            class="h-auto w-full rounded-xl object-contain"
            controls
          ></video>
          <p class="mt-3 text-xs text-black/50">{{ selectedItem?.name }}</p>
        </div>
      </div>
    </div>
  </teleport>
</template>
