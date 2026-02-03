<script setup lang="ts">
const menuItems = [
  { title: 'Intro', link: '#intro' },
  { title: 'Achievements', link: '#achiev' },
  { title: 'Gallery', link: '#gall' },
  { title: 'Location', link: '#loca' },
  { title: 'Guestbook', link: '#guest' },
] as const

const handleMenuClick = (event: MouseEvent, link: string) => {
  if (!link.startsWith('#')) return
  const target = document.querySelector(link)
  if (!target) return
  event.preventDefault()
  target.scrollIntoView({ behavior: 'smooth', block: 'start' })
}
</script>
<template>
  <ul
    class="sticky top-24 z-40 flex flex-nowrap overflow-x-auto gap-4 px-7 my-5 py-3 bg-white/80 backdrop-blur"
    role="menu"
  >
    <li
      v-for="item in menuItems"
      :key="item.title"
      role="none"
      class="shrink-0 px-4 py-2 rounded-md shadow-[3px_3px_20px_rgba(0,0,0,0.2)] font-bold cursor-pointer mx-2"
    >
      <a :href="item.link" role="menuitem" @click="handleMenuClick($event, item.link)">
        {{ item.title }}
      </a>
    </li>
  </ul>
</template>
