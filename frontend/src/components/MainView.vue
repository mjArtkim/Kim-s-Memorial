<script setup lang="ts">
import LanguageSelect from '@/components/unit/LanguageSelect.vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
</script>

<template>
  <LanguageSelect></LanguageSelect>
  <div>{{ t('app.title') }}</div>
</template>
