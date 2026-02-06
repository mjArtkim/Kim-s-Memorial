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
let lastViewportWidth = 0

gsap.registerPlugin(ScrollTrigger)

const scrollToTop = () => {
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

onMounted(() => {
  if (!photoRef.value || !miniBarRef.value || !heroRef.value) return
  ScrollTrigger.config({ ignoreMobileResize: true })

  const getMotionState = () => {
    const isDesktop = window.matchMedia('(min-width: 1024px)').matches
    const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    return { isDesktop, reduceMotion }
  }

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
    const { isDesktop, reduceMotion } = getMotionState()
    gsap.set(photoRef.value, {
      x: 0,
      y: 0,
      scale: 1,
      opacity: 1,
      clipPath: isDesktop && !reduceMotion ? 'circle(250% at 50% 50%)' : 'none',
    })
  }

  const updatePhotoTween = () => {
    if (!photoRef.value) return
    const { isDesktop, reduceMotion } = getMotionState()
    const photoRect = photoRef.value.getBoundingClientRect()
    const targetScale = isDesktop ? 0.8 : 0.94
    const targetY = -Math.round(photoRect.height * (isDesktop ? 0.12 : 0.06))
    if (photoTween) photoTween.kill()
    if (photoOpacityTween) photoOpacityTween.kill()
    if (reduceMotion) {
      gsap.set(photoRef.value, { clearProps: 'transform,opacity,clipPath' })
      return
    }
    const photoTweenVars: gsap.TweenVars = {
      x: 0,
      y: targetY,
      scale: targetScale,
      ease: 'none',
      scrollTrigger: {
        trigger: heroRef.value,
        start: 'top top',
        end: getHeroScrollEnd,
        scrub: 0.3,
        invalidateOnRefresh: true,
      },
    }
    if (isDesktop) {
      photoTweenVars.clipPath = 'circle(100% at 50% 50%)'
    }
    photoTween = gsap.to(photoRef.value, photoTweenVars)

    if (isDesktop) {
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
    } else {
      gsap.set(photoRef.value, { opacity: 1 })
    }
  }

  const syncPhotoAnimation = () => {
    applyStartSize()
    updatePhotoTween()
    ScrollTrigger.refresh()
  }

  lastViewportWidth = window.innerWidth
  syncPhotoAnimation()
  handleResize = () => {
    if (window.innerWidth === lastViewportWidth) return
    lastViewportWidth = window.innerWidth
    syncPhotoAnimation()
  }
  window.addEventListener('resize', handleResize)

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
  <div class="h-full py-9 lg:py-0">
    <div
      ref="stickyBarRef"
      class="fixed -top-1 left-0 right-0 z-40 flex flex-nowrap overflow-x-auto gap-4 px-7 mt-5bg-gradient-to-r bg-white backdrop-blur filter blur-sm h-32 opacity-0 lg:h-30"
    ></div>
    <div
      ref="miniBarRef"
      class="fixed left-1/2 top-4 z-50 inline-flex items-center gap-2.5 rounded-md bg-white/90 px-3 py-1.5 shadow-[0_6px_20px_rgba(0,0,0,0.08),0_1px_4px_rgba(0,0,0,0.08)] opacity-0 cursor-pointer lg:shadow-none"
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
      <div class="text-base font-semibold lg:text-xl">{{ t('app.title') }}</div>
    </div>
    <div class="h-screen grid grid-rows-[auto_1fr] gap-8 lg:pt-5 lg:block relative lg:h-full">
      <div class="hero-shell"></div>
      <LanguageSelect class="px-7 justify-self-end lg:absolute lg:top-5 lg:right-5"></LanguageSelect>
      <div ref="heroRef" class="grid scroll-mt-24 grid-rows-[auto_1fr] lg:flex lg:flex-row-reverse lg:justify-centers lg:items-end lg:h-[65vh] lg:ss-wrap">
        <div class="px-7 flex flex-col justify-center items-center gap-10 lg:flex-auto lg:items-start">
          <div class="text-6xl font-bold">Memorial</div> 
          <div class="text-5xl font-semibold">{{ t('app.title') }}</div>
          <div class="flex flex-col gap-10 justify-center items-center lg:items-start lg:flex-row">
            <div class="text-base">1948.09.30 ~ 2026.01.19</div>
            <div class="text-base">South Korea</div>
          </div>
        </div>
        <div class="lg:flex-auto flex lg:justify-center lg:ml-20">
          <div
            ref="photoRef"
            class="h-full w-full overflow-hidden origin-top transform-gpu [will-change:transform] lg:w-[340px] lg:h-[360px] lg:rounded-md lg:shadow-[0_12px_28px_rgba(0,0,0,0.12)]"
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
    <section class="lg:ss-wrap">
      <section class="flex flex-col items-center px-7 gap-12 scroll-mt-24 pb-10 lg:py-4 lg:gap-10">
        <div class="material-symbols-rounded text-[--mblue] text-5xl pt-4">candle</div>
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
      <section class="ss-wrap px-7 py-10">
        <div>
          <div class="text-[#8198A9]">© 2026, kimsmemorial</div>
          <div class="text-[#8198A9]">This memorial site was thoughtfully created by <a href="https://www.ideartm.com" target="_blank" class="font-bold lg:hover:text-[--mblue]">Minji Kim</a></div>
        </div>
      </section>
    </section>
  </div>
</template>

<style scoped>
.hero-shell {
  display: none;
}

@media (min-width: 1024px) {
  .hero-shell {
    position: absolute;
    display: block;
    content: '';
    clear: both;
    top: -5px;
    left: 0;
    width: 100%;
    background-image: url('@/assets/img/pc-bg.png');
    background-size: cover;
    background-position: center top;
    background-repeat: no-repeat;
    height: 300px;
    z-index: -5;
  }
}
</style>
