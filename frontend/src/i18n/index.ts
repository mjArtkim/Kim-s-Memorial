import { createI18n } from 'vue-i18n'

const messages = {
  en: {
    app: {
      title: "Kim's Memorial",
      description: 'A place to remember and celebrate',
    },
  },
  ko: {
    app: {
      title: '김의 추모관',
      description: '기억과 추모를 나누는 공간',
    },
  },
  'zh-Hans': {
    app: {
      title: '金的纪念馆',
      description: '纪念与追思的空间',
    },
  },
  'zh-Hant': {
    app: {
      title: '金的紀念館',
      description: '紀念與追思的空間',
    },
  },
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
