<script setup lang="ts">
import { useI18n } from 'vue-i18n'

const { locale } = useI18n()

const handleLocaleChange = (event: Event) => {
  const target = event.target as HTMLSelectElement | null
  if (!target) return
  const nextLocale = target.value
  localStorage.setItem('app-locale', nextLocale)
}
</script>

<template>
  <label class="inline-flex items-center gap-2 text-xs font-semibold">
    <div class="text-[var(--muted)] material-symbols-rounded">language</div>
    <div class="relative">
      <select
        class="appearance-none rounded-full border border-[var(--stroke)] bg-[var(--surface)] px-3 py-1 pr-7 text-xs font-semibold text-[var(--text)] focus:outline-none focus:border-neonpink"
        v-model="locale"
        @change="handleLocaleChange"
      >
        <option value="en">EN</option>
        <option value="ko">KR</option>
        <option value="zh-Hans">简体</option>
        <option value="zh-Hant">繁體</option>
      </select>
      <span
        class="material-symbols-rounded pointer-events-none absolute right-2 top-1/2 -translate-y-1/2 text-base text-[var(--muted)]"
      >
        expand_more
      </span>
    </div>
  </label>
</template>
