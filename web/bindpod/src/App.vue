<template>
  <div id="app">
    <router-view></router-view>
  </div>
</template>

<script>

export default {
  name: 'App',
  mounted() {
    if (!this.$cookie.get("Token")){
      this.$router.push("/login");
    }
  }
}
</script>

<style>
@import "assets/css/base.css";
#app {
  font-family: 'Helvetica', 'sans-serif', 'PingFangSC-Regular', 'PingFang SC';
  text-align: center;
  color: #FFFFFF;
  /*font-family: Avenir, Helvetica, Arial, sans-serif;*/
  /*-webkit-font-smoothing: antialiased;*/
  /*-moz-osx-font-smoothing: grayscale;*/
  /*text-align: center;*/
  /*color: #2c3e50;*/
  /*margin-top: 60px;*/
}
</style>
