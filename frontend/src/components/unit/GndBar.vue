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
    class="sticky top-24 z-40 flex flex-nowrap overflow-x-auto gap-4 px-7 my-5 py-3 bg-gradient-to-b lg:rounded-md lg:shadow-[0_5px_20px_rgba(0,0,0,0.1)] from-white/90 to-white/0 backdrop-blur lg:justify-center lg:ww-wrap lg:justify-evenly"
    role="menu"
  >
    <li
      v-for="item in menuItems"
      :key="item.title"
      role="none"
      class="shrink-0 px-4 py-2 rounded-md shadow-[3px_3px_20px_rgba(0,0,0,0.2)] font-semibold cursor-pointer mx-2 bg-white lg:shadow-none lg:py-1 lg:bg-white/0 lg:rounded-none"
    >
      <a :href="item.link" role="menuitem" @click="handleMenuClick($event, item.link)">
        {{ item.title }}
      </a>
    </li>
  </ul>
</template>
