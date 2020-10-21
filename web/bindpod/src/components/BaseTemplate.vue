<template>
  <div id="menu">
    <Header></Header>
    <div class="content">
      <el-container>
        <el-aside width="200px" style="background-color: rgb(238, 241, 246)">
          <el-menu :default-active="$route.path" router>

            <el-menu-item index="/domain"><i class="el-icon-menu"></i>域名列表</el-menu-item>
            <el-menu-item index="/add" v-show="is_superuser"><i class="el-icon-circle-plus"></i>添加域名</el-menu-item>
            <el-menu-item index="/user" v-show="is_superuser"><i class="el-icon-user-solid"></i>用户管理</el-menu-item>
            <el-menu-item index="/logs"><i class="el-icon-s-tools"></i>操作日志</el-menu-item>
          </el-menu>
        </el-aside>
        <el-container>
          <el-main>
            <div class="breadcrumb">
              <el-breadcrumb separator-class="el-icon-arrow-right">
                <el-breadcrumb-item :to="{ path: routerPath }">{{ routerName }}</el-breadcrumb-item>
                <el-breadcrumb-item v-if="currentRouterName">{{ currentRouterName }}</el-breadcrumb-item>
              </el-breadcrumb>
            </div>
            <slot name="main"></slot>
          </el-main>
        </el-container>
      </el-container>
    </div>
  </div>
</template>

<script>
import Header from "@/components/Header";

export default {
  name: "BaseTemplate",
  data(){
    return {
      is_superuser: this.$cookie.get('is_superuser')
    }
  },
  props: {
    routerPath: String,
    routerName: String,
    currentRouterName: String
  },
  components: {Header}
}
</script>

<style lang="scss" scoped>
#menu {
  .content {
    position: fixed;
    height: 100%;
    width: 100%;
  }
  .el-container, .el-menu {
    height: 100%;
    .el-main {
      padding: 10px;
    }
  }
  .breadcrumb {
    display: flex;
    width: 100%;
    background-color: #FFFFFF;
    height: 40px;
    margin-bottom: 10px;
    border-radius: 5px;

    .el-breadcrumb {
      height: 100%;
      line-height: 40px;
      margin-left: 20px;
    }
  }
}
</style>