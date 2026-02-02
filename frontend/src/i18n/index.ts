import { createI18n } from 'vue-i18n'
import en from './locales/en'
import ko from './locales/ko'
import zhHans from './locales/zh-Hans'
import zhHant from './locales/zh-Hant'

const messages = {
  en,
  ko,
  'zh-Hans': zhHans,
  'zh-Hant': zhHant,
}

export type MessageSchema = typeof messages

const i18n = createI18n({
  legacy: false,
  globalInjection: true,
  locale: 'en',
  fallbackLocale: 'en',
  messages,
})

export default i18n
