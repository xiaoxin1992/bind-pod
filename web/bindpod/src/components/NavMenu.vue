<template>
  <div class="menu">
      <el-menu class="el-menu-vertical" :default-active="$route.path" router>
        <el-menu-item index="/domain" class="menu-item">
          <i class="el-icon-s-home"></i>
          <span slot="title">域名管理</span>
        </el-menu-item>
        <el-menu-item index="/user" class="menu-item" v-if="is_superuser">
          <i class="el-icon-s-custom"></i>
          <span slot="title">用户管理</span>
        </el-menu-item>
        <el-menu-item index="/log" class="menu-item">
          <i class="el-icon-s-data"></i>
          <span slot="title">操作日志</span>
        </el-menu-item>
      </el-menu>
  </div>
</template>

<script>
import {mapState} from "vuex";

export default {
  name: "NavMenu",
  data() {
    return {
    }
  },
  computed: {
    ...mapState(['is_superuser']),
  },
}
</script>

<style scoped lang="scss">
.menu {
  //width: 227px;
  width: 100%;
  height: 100%;
  min-width: 227px;
  .el-menu-vertical{
    border-radius: 4px;
    height: 100%;
  }
}
</style>
