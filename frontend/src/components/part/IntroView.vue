<script setup lang="ts">
import { computed, onBeforeUnmount, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'

type Eulogy = {
  name: string
  title: string
  letter: string
}

const { t, tm } = useI18n()
const activeEulogyIndex = ref<number | null>(null)
const eulogies = computed<Eulogy[]>(() => {
  const value = tm('intro.eulogies')
  return Array.isArray(value) ? (value as Eulogy[]) : []
})
const activeEulogy = computed<Eulogy | null>(() => {
  if (activeEulogyIndex.value === null) return null
  return eulogies.value[activeEulogyIndex.value] ?? null
})
const isEulogyOpen = computed(() => activeEulogyIndex.value !== null)

const closeEulogy = () => {
  activeEulogyIndex.value = null
}

const openEulogy = (index: number) => {
  activeEulogyIndex.value = index
}

const handleKeydown = (event: KeyboardEvent) => {
  if (event.key !== 'Escape') return
  closeEulogy()
}

watch(isEulogyOpen, (isOpen) => {
  if (isOpen) {
    document.addEventListener('keydown', handleKeydown)
    document.body.style.overflow = 'hidden'
    return
  }
  document.removeEventListener('keydown', handleKeydown)
  document.body.style.overflow = ''
})

onBeforeUnmount(() => {
  document.removeEventListener('keydown', handleKeydown)
  document.body.style.overflow = ''
})
</script>
<template>
  <div>
    <div class="section-title">Intro</div>
    <div class="text-[18px] py-8">
      {{ t('intro.lorem') }}
    </div>
    <div>
      <div
        class="relative inline-block text-3xl font-semibold after:content-[''] after:absolute after:left-0 after:-bottom-4 after:h-[3px] after:w-full after:scale-x-100 after:bg-[--mblue]"
      >
        Eulogy
      </div>
      <ol class="mt-8 space-y-4">
        <li v-for="(eulogy, index) in eulogies" :key="`${eulogy.name}-${index}`">
          <button
            type="button"
            class="w-full text-left rounded-xl border border-black/10 px-5 py-4 shadow-[0_8px_20px_rgba(0,0,0,0.08)] transition hover:-translate-y-0.5 hover:shadow-[0_14px_24px_rgba(0,0,0,0.12)]"
            @click="openEulogy(index)"
          >
            <div class="flex items-center">
              <div class="text-xl font-semibold mr-3">{{ eulogy.name }}</div>
              <div class="text-sm text-black/60">{{ eulogy.title }}</div>
            </div>
            <div class="mt-3 text-sm font-semibold text-[--mblue]">
              {{ t('intro.openLetter') }}
            </div>
          </button>
        </li>
      </ol>
    </div>
  </div>
  <teleport to="body">
    <div
      v-if="isEulogyOpen"
      class="fixed inset-0 z-[100] flex items-center justify-center px-4 py-10"
      role="dialog"
      aria-modal="true"
      aria-label="Eulogy"
    >
      <button
        type="button"
        class="absolute inset-0 bg-black/50"
        :aria-label="t('intro.closeLetter')"
        @click="closeEulogy"
      ></button>
      <div
        class="relative w-full max-w-3xl rounded-2xl bg-white px-6 py-6 shadow-[0_20px_60px_rgba(0,0,0,0.22)]"
      >
        <div v-if="activeEulogy">
          <div class="flex items-center justify-between gap-6">
            <div class="flex items-center">
              <div class="text-xl font-semibold mr-3">{{ activeEulogy.name }}</div>
              <div class="text-sm text-black/60">{{ activeEulogy.title }}</div>
            </div>
            <button
              type="button"
              class="shrink-0 rounded-full border border-black/10 px-4 py-2 text-sm font-semibold transition hover:border-black/20 hover:bg-black/5"
              @click="closeEulogy"
            >
              {{ t('intro.closeLetter') }}
            </button>
          </div>
          <div class="mt-6 max-h-[70vh] space-y-6 overflow-y-auto pr-2">
            <p
              v-for="(para, i) in activeEulogy.letter.split('\n\n')"
              :key="i"
              class="mb-6 leading-7"
            >
              {{ para }}
            </p>
          </div>
        </div>
      </div>
    </div>
  </teleport>
</template>
