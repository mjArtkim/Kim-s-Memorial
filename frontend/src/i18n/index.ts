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

const getBrowserLocale = () => {
  if (typeof navigator === 'undefined') return null
  const languages = Array.isArray(navigator.languages) && navigator.languages.length
    ? navigator.languages
    : [navigator.language]
  for (const lang of languages) {
    const normalized = lang.toLowerCase()
    if (normalized.startsWith('ko')) return 'ko'
    if (normalized.startsWith('zh')) {
      if (
        normalized.includes('hant') ||
        normalized.includes('-tw') ||
        normalized.includes('-hk') ||
        normalized.includes('-mo')
      ) {
        return 'zh-Hant'
      }
      return 'zh-Hans'
    }
    if (normalized.startsWith('en')) return 'en'
  }
  return null
}

const getInitialLocale = () => {
  if (typeof window === 'undefined') return 'en'
  const savedLocale = localStorage.getItem('app-locale')
  if (savedLocale && Object.prototype.hasOwnProperty.call(messages, savedLocale)) {
    return savedLocale
  }
  const browserLocale = getBrowserLocale()
  if (browserLocale && Object.prototype.hasOwnProperty.call(messages, browserLocale)) {
    return browserLocale
  }
  return 'en'
}

const i18n = createI18n({
  legacy: false,
  globalInjection: true,
  locale: getInitialLocale(),
  fallbackLocale: 'en',
  messages,
})

export default i18n
