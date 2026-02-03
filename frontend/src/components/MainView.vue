<script setup lang="ts">
import LanguageSelect from '@/components/unit/LanguageSelect.vue'
import { useI18n } from 'vue-i18n'
import { nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { gsap } from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import GndBar from '@/components/unit/GndBar.vue'
import IntroView from '@/components/part/IntroView.vue'
import AchievementsView from '@/components/part/AchievementsView.vue'
import GalleryView from '@/components/part/GalleryView.vue'
import LocationView from '@/components/part/LocationView.vue'
import GuestbookView from '@/components/part/GuestbookView.vue'

const { t, locale } = useI18n()
const heroRef = ref<HTMLDivElement | null>(null)
const photoRef = ref<HTMLDivElement | null>(null)
const stickyBarRef = ref<HTMLDivElement | null>(null)
const miniBarRef = ref<HTMLDivElement | null>(null)
const miniAvatarRef = ref<HTMLDivElement | null>(null)
let photoTween: gsap.core.Tween | null = null
let photoOpacityTween: gsap.core.Tween | null = null
let handleResize: (() => void) | null = null
let isMiniBarVisible = false

gsap.registerPlugin(ScrollTrigger)

const scrollToTop = () => {
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

onMounted(() => {
  if (!photoRef.value || !miniBarRef.value || !heroRef.value) return

  const getHeroScrollEnd = () => {
    if (!heroRef.value) return '+=0'
    return `+=${Math.round(heroRef.value.offsetHeight * 1.5)}`
  }

  const getPhotoFadeStart = () => {
    if (!heroRef.value) return 'top top'
    return `top+=${Math.round(heroRef.value.offsetHeight * 1)} top`
  }

  const getMiniBarStart = () => {
    if (!heroRef.value) return 'top top'
    return `top+=${Math.round(heroRef.value.offsetHeight * 0.6)} top`
  }

  const applyStartSize = () => {
    if (!photoRef.value) return
    gsap.set(photoRef.value, {
      x: 0,
      y: 0,
      scale: 1,
      opacity: 1,
      clipPath: 'circle(250% at 50% 50%)',
    })
    ScrollTrigger.refresh()
  }

  applyStartSize()
  handleResize = () => {
    applyStartSize()
    updatePhotoTween()
  }
  window.addEventListener('resize', handleResize)

  const updatePhotoTween = () => {
    if (!photoRef.value) return
    const photoRect = photoRef.value.getBoundingClientRect()
    const targetScale = 0.8
    const targetY = -Math.round(photoRect.height * 0.12)
    if (photoTween) photoTween.kill()
    if (photoOpacityTween) photoOpacityTween.kill()
    photoTween = gsap.to(photoRef.value, {
      x: 0,
      y: targetY,
      scale: targetScale,
      clipPath: 'circle(100% at 50% 50%)',
      ease: 'none',
      scrollTrigger: {
        trigger: heroRef.value,
        start: 'top top',
        end: getHeroScrollEnd,
        scrub: 0.3,
        invalidateOnRefresh: true,
      },
    })

    photoOpacityTween = gsap.to(photoRef.value, {
      opacity: 0,
      ease: 'none',
      scrollTrigger: {
        trigger: heroRef.value,
        start: getPhotoFadeStart,
        end: 'bottom top',
        scrub: 0.3,
        invalidateOnRefresh: true,
      },
    })
  }

  updatePhotoTween()

  const showMiniBar = () => {
    if (!miniBarRef.value) return
    if (isMiniBarVisible) return
    isMiniBarVisible = true
    gsap.to(miniBarRef.value, {
      opacity: 1,
      y: 0,
      pointerEvents: 'auto',
      duration: 0.25,
      ease: 'power1.out',
      overwrite: 'auto',
    })
    if (stickyBarRef.value) {
      gsap.to(stickyBarRef.value, {
        opacity: 1,
        y: 0,
        pointerEvents: 'auto',
        duration: 0.25,
        ease: 'power1.out',
        overwrite: 'auto',
      })
    }
  }

  const hideMiniBar = () => {
    if (!miniBarRef.value) return
    if (!isMiniBarVisible) return
    isMiniBarVisible = false
    gsap.to(miniBarRef.value, {
      opacity: 0,
      y: -10,
      pointerEvents: 'none',
      duration: 0.2,
      ease: 'power1.out',
      overwrite: 'auto',
    })
    if (stickyBarRef.value) {
      gsap.to(stickyBarRef.value, {
        opacity: 0,
        y: -12,
        pointerEvents: 'none',
        duration: 0.2,
        ease: 'power1.out',
        overwrite: 'auto',
      })
    }
  }

  if (stickyBarRef.value) {
    gsap.set(stickyBarRef.value, {
      opacity: 0,
      y: -12,
      pointerEvents: 'none',
    })
  }
  gsap.set(miniBarRef.value, {
    opacity: 0,
    y: -10,
    x: 0,
    xPercent: -50,
    pointerEvents: 'none',
  })
  ScrollTrigger.create({
    trigger: heroRef.value,
    start: getMiniBarStart,
    end: 'bottom top',
    onEnter: showMiniBar,
    onLeaveBack: hideMiniBar,
    invalidateOnRefresh: true,
  })

  ScrollTrigger.refresh()
})

onBeforeUnmount(() => {
  if (photoTween) {
    photoTween.kill()
    photoTween = null
  }
  if (photoOpacityTween) {
    photoOpacityTween.kill()
    photoOpacityTween = null
  }
  if (handleResize) {
    window.removeEventListener('resize', handleResize)
    handleResize = null
  }
  ScrollTrigger.getAll().forEach((trigger) => trigger.kill())
})

watch(
  locale,
  async (nextLocale) => {
    document.documentElement.lang = nextLocale
    localStorage.setItem('app-locale', nextLocale)
    await nextTick()
    if (miniBarRef.value) {
      gsap.set(miniBarRef.value, { x: 0, xPercent: -50 })
    }
  },
  { immediate: true },
)
</script>

<template>
  <div class="h-full py-9">
    <div
      ref="stickyBarRef"
      class="fixed top-0 left-0 right-0 z-40 flex flex-nowrap overflow-x-auto gap-4 px-7 mt-5bg-gradient-to-r from-white/0 to-white backdrop-blur filter blur-sm h-32 opacity-0"
    ></div>
    <div
      ref="miniBarRef"
      class="fixed left-1/2 top-7 z-50 inline-flex items-center gap-2.5 rounded-md bg-white/90 px-3 py-1.5 shadow-[0_6px_20px_rgba(0,0,0,0.08),0_1px_4px_rgba(0,0,0,0.08)] opacity-0 cursor-pointer"
      role="button"
      tabindex="0"
      aria-label="Scroll to top"
      @click="scrollToTop"
    >
      <div ref="miniAvatarRef" class="h-12 w-12 overflow-hidden rounded-md border border-black/10">
        <img
          src="@/assets/img/main.png"
          alt="Main Photo"
          class="h-full w-full object-cover block"
        />
      </div>
      <div class="text-base font-semibold">{{ t('app.title') }}</div>
    </div>
    <div class="h-screen grid grid-rows-[auto_1fr] gap-8">
      <LanguageSelect class="px-7 justify-self-end"></LanguageSelect>
      <div ref="heroRef" id="intro" class="grid scroll-mt-24 grid-rows-[auto_1fr]">
        <div class="px-7 flex flex-col justify-center items-center gap-10">
          <div class="text-6xl font-bold">Memorial</div>
          <div class="text-5xl font-semibold">{{ t('app.title') }}</div>
          <div class="text-base">1948.09.30 ~ 2026.01.19</div>
          <div class="text-base">South Korea</div>
        </div>
        <div>
          <div
            ref="photoRef"
            class="h-full w-full overflow-hidden origin-top [will-change:transform]"
          >
            <img
              src="@/assets/img/main.png"
              alt="Main Photo"
              class="h-full w-full object-cover block"
            />
          </div>
        </div>
      </div>
    </div>
    <section class="flex flex-col items-center px-7 gap-12 scroll-mt-24 pb-10">
      <div class="material-symbols-rounded text-[--mblue] text-5xl">candle</div>
      <div class="text-center text-[18px]">
        {{ t('app.description') }}
      </div>
    </section>
    <GndBar />
    <section id="intro" class="p-7 scroll-mt-24">
      <IntroView />
    </section>
    <section id="achiev" class="p-7 scroll-mt-24">
      <AchievementsView />
    </section>
    <section id="gall" class="p-7 scroll-mt-24">
      <GalleryView />
    </section>
    <section id="loca" class="p-7 scroll-mt-24">
      <LocationView />
    </section>
    <section id="guest" class="p-7 scroll-mt-24">
      <GuestbookView />
    </section>
  </div>
</template>
