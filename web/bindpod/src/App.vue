<template>
  <div id="app">
    <router-view></router-view>
  </div>
</template>

<script>
export default {
  name: 'App',
  components: {
  },
  mounted() {
    this.getCookie();
  },
  methods: {
    getCookie(){
      let userInfoStr = this.$cookie.get("userinfo")
      if (userInfoStr === null) {
        this.$router.push('/login');
        return false;
      }
      try {
        let userinfo = JSON.parse(userInfoStr);
        if (userinfo === null) {
          this.$router.push('/login');
        }
        this.$store.dispatch("saveUserName", {"username": userinfo.username, "display_name": userinfo.display_name, "is_superuser": userinfo.is_superuser});
      }catch (exception) {
        this.$router.push('/login');
        return false;
      }
    }
  },
}
</script>

<style lang="scss">
@import "assets/css/base.css";
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  font-size: 16px;
  min-width: 300px;
/*  -webkit-font-smoothing: antialiased;*/
/*  -moz-osx-font-smoothing: grayscale;*/
/*  text-align: center;*/
/*  color: #2c3e50;*/
/*  margin-top: 60px;*/
}
</style>
