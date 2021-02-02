<template>
  <div class="index">
    <el-container style="height: 100vh;">
      <el-header><nav-header></nav-header></el-header>
      <el-container>
        <el-aside width="230px">
          <nav-menu></nav-menu>
        </el-aside>
        <el-main style="height: 100%">
          <el-row class="content">
            <el-col class="title">
              <el-breadcrumb separator-class="el-icon-arrow-right">
                <el-breadcrumb-item v-if="$route.meta.parent" :to="{ path: $route.meta.parentPath }">{{ $route.meta.parent }}</el-breadcrumb-item>
                <el-breadcrumb-item>{{ $route.meta.name }}</el-breadcrumb-item>
              </el-breadcrumb>
            </el-col>
            <el-col class="router">
              <router-view></router-view>
            </el-col>
          </el-row>
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script>
import NavHeader from "@/components/NavHeader";
import NavMenu from "@/components/NavMenu";
export default {
  name: "index",
  data() {
    return {
      title: ""
    }
  },
  mounted() {
    this.title = "1100"
  },
  components: {
    NavMenu,
    NavHeader
  }
}
</script>

<style scoped lang="scss">
.index {
  .el-header {
    min-width: 1520px;
    background-color: #409EFF;
    line-height: 60px;
  }

  .el-aside {
    text-align: center;
  }
  .el-main {
    min-width: 1300px;
    padding: 10px 0 0 10px;
    .content, .title, .router {
      height: 100%;
      width: 100%;
    }
    .title {
      height: 40px;
      border-radius: 4px;
      background-color: #FFFFFF;
      padding-left: 20px;
      margin-bottom: 10px;
      .el-breadcrumb {
        height: 100%;
        line-height: 40px;
      }
    }
    .router {
      height: calc(100% - 40px);
      background-color: #FFFFFF;
      border-radius: 4px;
    }
  }
}
</style>
