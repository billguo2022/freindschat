<template>
  <router-view></router-view>
</template>

<script setup>
</script>

<style lang='scss'>
@import url("https://fonts.googleapis.com/css?family=Fira+Sans");

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html,
body {
  width: 100vw;
  height: 100vh;
  margin: 0;
  font-family: "Fira Sans", Helvetica, Arial, sans-serif;
}

#app {
  height: 100vh;
  width: 100vw;
}
</style>