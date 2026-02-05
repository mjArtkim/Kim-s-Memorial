<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'

type MapKey = 'google' | 'kakao' | 'osm'
type MapConfig = {
  label: string
  embedUrl: string
  shareUrl: string
}

const { t } = useI18n()
const activeMap = ref<MapKey>('google')

const mapCenter = { lat: 37.291218, lng: 127.08295 }
const mapZoom = 19
const mapQuery = computed(() => t('location.mapQuery'))
const mapFrameRef = ref<HTMLDivElement | null>(null)
const frameSize = ref({ width: 320, height: 260 })
let resizeObserver: ResizeObserver | null = null
const kakaoStaticMap = {
  linkUrl:
    'https://map.kakao.com/?urlX=518385&urlY=1053337&urlLevel=3&map_type=TYPE_MAP&map_hybrid=false',
  imageUrl:
    'https://staticmap.kakao.com/map/mapservice?FORMAT=PNG&SCALE=2.5&MX=518382&MY=1053335&S=0&IW=504&IH=310&LANG=0&COORDSTM=WCONGNAMUL&logo=kakao_logo',
  logoUrl:
    'https://t1.daumcdn.net/localimg/localimages/07/2018/pc/common/logo_kakaomap.png',
}

const updateFrameSize = () => {
  if (!mapFrameRef.value) return
  const rect = mapFrameRef.value.getBoundingClientRect()
  frameSize.value = {
    width: Math.max(1, Math.round(rect.width)),
    height: Math.max(1, Math.round(rect.height)),
  }
}

const toRadians = (deg: number) => (deg * Math.PI) / 180
const toDegrees = (rad: number) => (rad * 180) / Math.PI

const project = (lat: number, lng: number, zoom: number) => {
  const scale = 256 * Math.pow(2, zoom)
  const sinLat = Math.sin(toRadians(lat))
  const x = ((lng + 180) / 360) * scale
  const y = (0.5 - Math.log((1 + sinLat) / (1 - sinLat)) / (4 * Math.PI)) * scale
  return { x, y, scale }
}

const unproject = (x: number, y: number, scale: number) => {
  const lng = (x / scale) * 360 - 180
  const y2 = 0.5 - y / scale
  const lat = toDegrees(Math.atan(Math.sinh(Math.PI * (1 - 2 * y2))))
  return { lat, lng }
}

const osmBBox = computed(() => {
  const { width, height } = frameSize.value
  const { x, y, scale } = project(mapCenter.lat, mapCenter.lng, mapZoom)
  const halfW = width / 2
  const halfH = height / 2
  const leftTop = unproject(x - halfW, y - halfH, scale)
  const rightBottom = unproject(x + halfW, y + halfH, scale)
  return {
    left: leftTop.lng.toFixed(6),
    bottom: rightBottom.lat.toFixed(6),
    right: rightBottom.lng.toFixed(6),
    top: leftTop.lat.toFixed(6),
  }
})

const mapTabs = computed(() => [
  { key: 'google' as MapKey, label: t('location.tabs.google') },
  { key: 'kakao' as MapKey, label: t('location.tabs.kakao') },
  { key: 'osm' as MapKey, label: t('location.tabs.osm') },
])

const mapConfig = computed<Record<MapKey, MapConfig>>(() => {
  const query = encodeURIComponent(mapQuery.value)
  const { lat, lng } = mapCenter
  const { left, bottom, right, top } = osmBBox.value
  return {
    google: {
      label: t('location.tabs.google'),
      embedUrl: `https://maps.google.com/maps?q=${query}&z=${mapZoom}&output=embed`,
      shareUrl: `https://maps.google.com/?q=${query}`,
    },
    kakao: {
      label: t('location.tabs.kakao'),
      embedUrl: '',
      shareUrl: kakaoStaticMap.linkUrl,
    },
    osm: {
      label: t('location.tabs.osm'),
      embedUrl: `https://www.openstreetmap.org/export/embed.html?bbox=${left}%2C${bottom}%2C${right}%2C${top}&layer=mapnik&marker=${lat}%2C${lng}`,
      shareUrl: `https://www.openstreetmap.org/?mlat=${lat}&mlon=${lng}#map=${mapZoom}/${lat}/${lng}`,
    },
  }
})

const activeConfig = computed(() => mapConfig.value[activeMap.value])

const infoItems = computed(() => [
  {
    icon: 'location_on',
    title: t('location.placeName'),
    subtitle: t('location.placeSub'),
  },
  {
    icon: 'pin_drop',
    title: `${t('location.plotLabel')}: ${t('location.plotValue')}`,
  },
])

onMounted(() => {
  updateFrameSize()
  if (typeof ResizeObserver !== 'undefined') {
    resizeObserver = new ResizeObserver(() => updateFrameSize())
    if (mapFrameRef.value) resizeObserver.observe(mapFrameRef.value)
  } else {
    window.addEventListener('resize', updateFrameSize)
  }
})

onBeforeUnmount(() => {
  if (resizeObserver) {
    resizeObserver.disconnect()
    resizeObserver = null
  } else {
    window.removeEventListener('resize', updateFrameSize)
  }
})
</script>
<template>
  <div class="space-y-8">
    <div class="section-title">{{ t('location.title') }}</div>
    <div class="flex flex-wrap gap-3 pt-7">
      <button
        v-for="tab in mapTabs"
        :key="tab.key"
        type="button"
        class="rounded-xl font-semibold bg-white px-5 py-2 shadow-[3px_3px_10px_rgba(0,0,0,0.12)] transition"
        :class="
          activeMap === tab.key
            ? 'border-[--mdark] border text-[--mdark]'
            : 'text-black/70 hover:border-black/20'
        "
        :aria-pressed="activeMap === tab.key"
        @click="activeMap = tab.key"
      >
        {{ tab.label }}
      </button>
    </div>

    <div
      class="rounded-2xl border border-black/10 bg-white shadow-[0_12px_28px_rgba(0,0,0,0.12)] overflow-hidden"
    >
      <div ref="mapFrameRef" class="relative h-[260px] sm:h-[320px]">
        <a
          :href="activeConfig.shareUrl"
          target="_blank"
          rel="noreferrer"
          class="absolute right-3 top-3 z-10 inline-flex items-center gap-2 rounded-full border border-black/10 bg-white/90 px-3 py-1.5 text-xs font-semibold text-[--mdark] shadow-[0_6px_16px_rgba(0,0,0,0.12)] backdrop-blur transition hover:border-black/20"
        >
          <span class="material-symbols-rounded text-base">open_in_new</span>
          {{ t('location.openMap') }}
        </a>
        <div v-if="activeMap === 'kakao'" class="flex h-full w-full flex-col">
          <a
            :href="kakaoStaticMap.linkUrl"
            target="_blank"
            rel="noreferrer"
            class="block flex-1"
          >
            <img
              :src="kakaoStaticMap.imageUrl"
              :alt="t('location.kakaoAlt')"
              class="h-full w-full object-cover"
            />
          </a>
          <div
            class="flex items-center justify-between gap-3 border-t border-black/10 bg-white/90 px-3 py-2 text-[11px] font-semibold text-black/70"
          >
            <img :src="kakaoStaticMap.logoUrl" :alt="t('location.kakaoAlt')" class="h-4" />
            <a
              :href="kakaoStaticMap.linkUrl"
              target="_blank"
              rel="noreferrer"
              class="text-black/70 transition hover:text-black"
            >
              {{ t('location.kakaoLarge') }}
            </a>
          </div>
        </div>
        <iframe
          v-else-if="activeConfig.embedUrl"
          :key="activeMap"
          :src="activeConfig.embedUrl"
          class="block h-full w-full border-0"
          loading="lazy"
          referrerpolicy="no-referrer-when-downgrade"
          allowfullscreen
          :aria-label="t('location.mapLabel', { provider: activeConfig.label })"
        ></iframe>
        <div
          v-else
          class="h-full w-full flex flex-col items-center justify-center gap-3 bg-[radial-gradient(circle_at_top,#f5f7ff,#ffffff)]"
        >
          <div class="text-lg font-semibold text-black/70">
            {{ t('location.embedFallbackTitle', { provider: activeConfig.label }) }}
          </div>
          <p class="text-sm text-black/50 text-center px-6">
            {{ t('location.embedFallbackDescription') }}
          </p>
          <a
            :href="activeConfig.shareUrl"
            target="_blank"
            rel="noreferrer"
            class="inline-flex items-center gap-2 rounded-full border border-[--mblue] bg-white px-4 py-2 text-sm font-semibold text-[--mdark] transition hover:border-[--mdark]"
          >
            <span class="material-symbols-rounded text-base">open_in_new</span>
            {{ t('location.openMap') }}
          </a>
        </div>
      </div>
    </div>

    <div
      class="rounded-2xl border border-black/10 bg-white px-6 py-6 shadow-[0_12px_30px_rgba(0,0,0,0.12)]"
    >
      <div class="text-xl font-semibold">{{ t('location.infoTitle') }}</div>
      <p class="mt-4 text-black/60 leading-7">
        {{ t('location.description') }}
      </p>
      <div class="mt-6 space-y-4">
        <div v-for="(item, index) in infoItems" :key="index" class="flex items-start gap-3">
          <span class="material-symbols-rounded text-[--mdark] text-xl">{{ item.icon }}</span>
          <div>
            <div class="font-semibold text-black/80">{{ item.title }}</div>
            <div v-if="item.subtitle" class="text-sm text-black/60">{{ item.subtitle }}</div>
          </div>
        </div>
      </div>
      <a
        :href="activeConfig.shareUrl"
        target="_blank"
        rel="noreferrer"
        class="mt-6 inline-flex items-center gap-2 text-sm font-semibold text-[--mdark] transition hover:text-black"
      >
        <span class="material-symbols-rounded text-base">link</span>
        <span>{{ t('location.shareLabel') }}</span>
      </a>
    </div>
  </div>
</template>
