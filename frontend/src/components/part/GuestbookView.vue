<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'

type GuestbookEntry = {
  id: number
  date: string
  content: string
  name: string
  highlight?: boolean
}

const { t } = useI18n()

const isModalOpen = ref(false)
const nameValue = ref('')
const contentValue = ref('')
const isLoading = ref(true)
const hasError = ref(false)
const isSubmitting = ref(false)
const submitError = ref(false)

const entries = ref<GuestbookEntry[]>([])

const canSubmit = computed(
  () => nameValue.value.trim().length > 0 && contentValue.value.trim().length > 0,
)

const openModal = () => {
  isModalOpen.value = true
  submitError.value = false
}

const closeModal = () => {
  isModalOpen.value = false
  submitError.value = false
}

const formatDate = (date: Date) => {
  const day = `${date.getDate()}`.padStart(2, '0')
  const month = `${date.getMonth() + 1}`.padStart(2, '0')
  const year = date.getFullYear()
  return `${day}.${month}.${year}`
}

const formatDateValue = (value: string | Date) => {
  if (value instanceof Date) return formatDate(value)
  const normalized = value.includes('T') ? value : value.replace(' ', 'T')
  const parsed = new Date(normalized)
  if (Number.isNaN(parsed.getTime())) return value
  return formatDate(parsed)
}

const fetchGuestbook = async () => {
  isLoading.value = true
  hasError.value = false
  try {
    const response = await fetch('/api/guestbook')
    if (!response.ok) throw new Error('Failed to fetch guestbook')
    const data = await response.json()
    const list = Array.isArray(data) ? data : []
    const mapped = list
      .map((item) => {
        if (!item) return null
        const id =
          typeof item.id === 'number'
            ? item.id
            : Number.isFinite(Number(item.id))
              ? Number(item.id)
              : Date.now()
        const name = typeof item.name === 'string' ? item.name : ''
        const content = typeof item.content === 'string' ? item.content : ''
        const createdAt =
          typeof item.created_at === 'string' ? item.created_at : new Date().toISOString()
        return {
          id,
          name,
          content,
          date: formatDateValue(createdAt),
        }
      })
      .filter((item): item is GuestbookEntry => item !== null)
    entries.value = mapped
  } catch (error) {
    hasError.value = true
    entries.value = []
  } finally {
    isLoading.value = false
  }
}

const submitEntry = async () => {
  if (!canSubmit.value || isSubmitting.value) return
  isSubmitting.value = true
  submitError.value = false
  try {
    const payload = {
      name: nameValue.value.trim(),
      content: contentValue.value.trim(),
    }
    const response = await fetch('/api/guestbook', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
    if (!response.ok) throw new Error('Failed to submit guestbook entry')
    nameValue.value = ''
    contentValue.value = ''
    closeModal()
    await fetchGuestbook()
  } catch (error) {
    submitError.value = true
  } finally {
    isSubmitting.value = false
  }
}

const handleKeydown = (event: KeyboardEvent) => {
  if (event.key !== 'Escape') return
  closeModal()
}

watch(isModalOpen, (isOpen) => {
  if (isOpen) {
    document.addEventListener('keydown', handleKeydown)
    document.body.style.overflow = 'hidden'
    return
  }
  document.removeEventListener('keydown', handleKeydown)
  document.body.style.overflow = ''
})

onMounted(() => {
  fetchGuestbook()
})

onBeforeUnmount(() => {
  document.removeEventListener('keydown', handleKeydown)
  document.body.style.overflow = ''
})
</script>
<template>
  <div class="space-y-6">
    <div class="space-y-3">
      <div class="section-title">{{ t('guestbook.title') }}</div>
      <p class="text-black/50">{{ t('guestbook.description') }}</p>
    </div>

    <button
      type="button"
      class="w-full rounded-xl border-black/10 bg-white px-5 py-3 text-sm font-semibold shadow-[0_8px_18px_rgba(0,0,0,0.1)] transition hover:-translate-y-0.5 hover:shadow-[0_14px_26px_rgba(0,0,0,0.14)]"
      @click="openModal"
    >
      <span class="inline-flex items-center gap-2">
        <span class="material-symbols-rounded text-[--mdark] text-xl">edit_note</span>
        <span>{{ t('guestbook.write') }}</span>
      </span>
    </button>

    <div
      v-if="isLoading"
      class="rounded-2xl border border-dashed border-black/10 py-16 text-center"
    >
      <p class="text-black/50">{{ t('guestbook.loading') }}</p>
    </div>
    <div
      v-else-if="hasError"
      class="rounded-2xl border border-dashed border-black/10 py-16 text-center"
    >
      <p class="text-black/50">{{ t('guestbook.error') }}</p>
    </div>
    <div
      v-else-if="entries.length === 0"
      class="rounded-2xl border border-dashed border-black/10 py-16 text-center"
    >
      <p class="text-black/50">{{ t('guestbook.empty') }}</p>
    </div>

    <div v-else class="space-y-5">
      <article
        v-for="entry in entries"
        :key="entry.id"
        class="rounded-2xl border bg-white px-5 py-5 shadow-[0_8px_20px_rgba(0,0,0,0.08)]"
      >
        <div class="text-sm font-semibold text-black/70">
          {{ entry.date }}
        </div>
        <p class="mt-3 whitespace-pre-line text-[15px] leading-6 text-black/70">
          {{ entry.content }}
        </p>
        <div class="mt-6 text-right text-sm font-semibold text-black/70">
          {{ entry.name }}
        </div>
      </article>
    </div>
  </div>

  <teleport to="body">
    <div
      v-if="isModalOpen"
      class="fixed inset-0 z-[120] flex items-center justify-center px-5 py-10"
      role="dialog"
      aria-modal="true"
      :aria-label="t('guestbook.write')"
    >
      <button
        type="button"
        class="absolute inset-0 bg-black/40"
        :aria-label="t('guestbook.cancel')"
        @click="closeModal"
      ></button>
      <div
        class="relative w-full max-w-sm rounded-2xl bg-white px-5 py-5 shadow-[0_18px_50px_rgba(0,0,0,0.25)]"
      >
        <div class="flex items-center gap-2 text-base font-semibold">
          <span class="material-symbols-rounded text-[--mdark]">edit_note</span>
          <span>{{ t('guestbook.write') }}</span>
        </div>
        <div class="mt-5 space-y-5">
          <div>
            <label class="text-xs font-semibold text-black/60">{{
              t('guestbook.nameLabel')
            }}</label>
            <input
              v-model="nameValue"
              type="text"
              class="mt-2 w-full border-b border-black/20 bg-transparent pb-2 text-sm outline-none placeholder:text-black/40"
              :placeholder="t('guestbook.namePlaceholder')"
            />
          </div>
          <div>
            <label class="text-xs font-semibold text-black/60">{{
              t('guestbook.contentLabel')
            }}</label>
            <textarea
              v-model="contentValue"
              rows="6"
              class="mt-2 w-full resize-none border-b border-black/20 bg-transparent pb-2 text-sm outline-none placeholder:text-black/40"
              :placeholder="t('guestbook.contentPlaceholder')"
            ></textarea>
          </div>
        </div>
        <p v-if="submitError" class="mt-3 text-xs font-semibold text-red-500">
          {{ t('guestbook.submitError') }}
        </p>
        <div class="mt-6 flex items-center justify-end gap-2">
          <button
            type="button"
            class="rounded-full border border-black/10 px-4 py-2 text-xs font-semibold text-black/50 transition hover:text-black/70"
            @click="closeModal"
          >
            {{ t('guestbook.cancel') }}
          </button>
          <button
            type="button"
            class="rounded-full bg-[--mdark] px-4 py-2 text-xs font-semibold text-white transition disabled:cursor-not-allowed disabled:opacity-40"
            :disabled="!canSubmit || isSubmitting"
            @click="submitEntry"
          >
            {{ t('guestbook.submit') }}
          </button>
        </div>
      </div>
    </div>
  </teleport>
</template>
