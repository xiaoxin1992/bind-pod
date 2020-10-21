<template>
  <div id="login">
    <el-container>
      <el-main>
        <div class="form">
          <el-row>
            <div class="title">BindPod登陆</div>
          </el-row>
          <el-row>
            <el-input v-model="username" size="medium" placeholder="请输入用户名"></el-input>
          </el-row>
          <el-row>
            <el-input v-model="password" show-password size="medium" placeholder="请输入密码"></el-input>
          </el-row>
          <el-row>
            <el-button size="medium" type="primary" @click="login">登陆</el-button>
          </el-row>
        </div>
      </el-main>
      <el-footer height="60px">BindPod</el-footer>
    </el-container>
  </div>
</template>

<script>
export default {
  name: "login",
  data() {
    return {
      username: '',
      password: ''
    }
  },
  methods: {
    login() {
      let {username, password} = this;
      this.axios.post('/login/', {
        username,
        password
      }).then((res) => {
        this.$cookie.set("Token", "Token " + res.data.Token, {
          expires: 'Session'
        })
        this.$cookie.set("user", res.data.username, {
          expires: 'Session'
        })
        this.$cookie.set("username", res.data.display_name, {
          expires: 'Session'
        })
        if (res.data.is_superuser) {
          this.$cookie.set("is_superuser", res.data.is_superuser, {
            expires: 'Session'
          })
        }

        this.$router.push('/');
      }).catch((err) => {
        this.$message({
          message: err.data.msg.detail,
          type: "error"
        });
      });

      // this.axios.post('/login/', {
      //   username,
      //   password
      // }).then((res)=>{
      //   console.log(res);
      //   this.$store.dispatch('saveUser', res)
      //   return;
      // }).catch((err)=>{
      //   console.log("===============")
      //   this.$message({
      //     message: err.data.msg.detail,
      //     "type": "error"
      //   });
      // })
      // this.$message({
      //   message: '密码错误',
      //   type: 'error'
      // });
      // this.axios.post('/login/', {
      //   username: "root",
      //   password: "root"
      // }).then((respon)=>{
      //   console.log(respon)
      // }).catch(err=>{
      //   console.log(err)
      // })
      // this.$router.push('/');
    }
  }
}
</script>

<style lang="scss" scoped>
.el-container {
  width: 100%;
  height: 100%;

  .form {
    background-color: #FFFFFF;
    width: 375px;
    height: 320px;
    margin: 200px auto 130px auto;
    border-radius: 5px;
    box-shadow: 0 0 6px rgba(0, 0, 0, 0.1);
    border: #FFFFFF solid 1px;

    .title {
      color: #606266;
      font-size: 24px;
      font-style: normal;
      margin-top: 30px;
    }

    .el-input {
      width: 250px;
      margin-top: 30px;
    }

    .el-button {
      margin-top: 40px;
      width: 250px;
    }
  }
}

</style>