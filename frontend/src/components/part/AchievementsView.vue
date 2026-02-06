<script setup lang="ts">
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'

type AchievementItem = {
  title: string
  summary: string
  bullets: string[]
}

const { t, tm } = useI18n()
const achievements = computed<AchievementItem[]>(() => {
  const value = tm('achievements.items')
  return Array.isArray(value) ? (value as AchievementItem[]) : []
})

const openIndex = ref<number | null>(null)

const toggleAchievement = (index: number) => {
  openIndex.value = openIndex.value === index ? null : index
}

const isOpen = (index: number) => openIndex.value === index
</script>
<template>
  <div class="space-y-6">
    <div class="space-y-4">
      <div class="section-title">{{ t('achievements.title') }}</div>
      <p class="text-[--mblue]">
        {{ t('achievements.description') }}
      </p>
    </div>
    <div class="space-y-6">
      <article
        v-for="(item, index) in achievements"
        :key="`${item.title}-${index}`"
        class="rounded-xl border border-black/10 bg-white px-6 py-5 shadow-[3px_3px_24px_rgba(0,0,0,0.1)]"
      >
        <div class="grid grid-cols-[1fr_0.2fr] items-center">
          <div class="text-xl font-semibold text-black/90">
            {{ item.title }}
          </div>
          <button
            type="button"
            class="w-full text-right text-sm text-[--mblue] transition hover:text-[--mdark] hidden lg:block"
            :aria-expanded="isOpen(index)"
            :aria-controls="`achievement-details-${index}`"
            @click="toggleAchievement(index)"
          >
            {{ isOpen(index) ? t('achievements.showLess') : t('achievements.show') }}
          </button>
        </div>
        <div class="mt-3 font-medium text-black/50">
          {{ item.summary }}
        </div>
        <div v-if="isOpen(index)" :id="`achievement-details-${index}`" class="mt-4 space-y-5">
          <ul class="space-y-4 text-black/70">
            <li v-for="(bullet, bulletIndex) in item.bullets" :key="bulletIndex">
              <div class="flex items-start gap-3">
                <span class="mt-2 h-2 w-2 rounded-full bg-[--mdark]"></span>
                <span class="leading-6">{{ bullet }}</span>
              </div>
            </li>
          </ul>
        </div>
          <button
            type="button"
            class="w-full text-right text-sm text-[--mblue] transition hover:text-[--mdark] lg:hidden"
            :aria-expanded="isOpen(index)"
            :aria-controls="`achievement-details-${index}`"
            @click="toggleAchievement(index)"
          >
            {{ isOpen(index) ? t('achievements.showLess') : t('achievements.show') }}
          </button>
      </article>
    </div>
  </div>
</template>
