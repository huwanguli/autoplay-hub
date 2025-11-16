<script setup>
import { RouterView } from 'vue-router'
</script>

<template>
  <header>
    <div class="wrapper">
      <h1>AutoPlay Hub</h1>
    </div>
  </header>

  <main>
    <RouterView />
  </main>
</template>

<style scoped>
/* scoped 样式意味着这里的CSS只对当前组件(App.vue)生效，不会影响到其他地方 */
header {
  line-height: 1.5;
  background-color: #f8f9fa;
  padding: 1rem 2rem;
  border-bottom: 1px solid #dee2e6;
}

h1 {
  font-size: 1.5rem;
  font-weight: 500;
  color: #212529;
}

main {
  padding: 2rem;
}
</style>
