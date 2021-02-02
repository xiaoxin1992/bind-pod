<template>
  <div class="login">
    <el-container>
      <el-main>
        <div class="main-container">
          <div class="form">
            <el-row>
              <el-col>
                <div class="title">BindPod登陆</div>
              </el-col>
              <el-col>
                <el-form :model="form" status-icon :rules="rules" ref="form">
                  <el-form-item prop="username">
                    <el-input class="input" validate-event clearable v-model="form.username"
                              size="medium" placeholder="请输入用户名"></el-input>
                  </el-form-item>
                  <el-form-item prop="password">
                    <el-input class="input" validate-event clearable v-model="form.password"
                              size="medium" show-password placeholder="请输入密码"></el-input>
                  </el-form-item>
                  <el-button class="input" size="medium" type="primary" @click="login">登陆</el-button>
                </el-form>
              </el-col>
            </el-row>
          </div>
        </div>
      </el-main>
    </el-container>
  </div>
</template>

<script>
export default {
  name: "login",
  data() {
    let checkLogin = (rule, value, callback) => {
      if (value === '') {
        switch (rule.field) {
          case 'username':
            callback(new Error('用户名不能为空'));
            break;
          case 'password':
            callback(new Error('密码不能为空'));
            break;
        }
      }
      callback();
    };
    return {
      form: {
        'username': '',
        'password': ''
      },
      rules: {
        username: [{validator: checkLogin, trigger: 'blur'}],
        password: [{validator: checkLogin, trigger: 'blur'}],
      },
    }
  },
  methods: {
    login() {
      let {username, password} = this.form;
      if (username.trim().length === 0 || password.trim().length === 0) {
        this.$refs.form.validateField('username');
        this.$refs.form.validateField('password');
        return;
      }
      this.axios.post('/login/', {
        username,
        password
      }).then((res) => {
        let data = {
          username: res.data.username,
          display_name: res.data.display_name,
          is_superuser: res.data.is_superuser
        }
        this.$cookie.set('token', `Token ${res.data.Token}`, {expires: 'Session'})
        this.$cookie.set('userinfo', JSON.stringify(data), {expires: 'Session'})
        this.$store.dispatch("saveUserName", {"username": res.data.username, "display_name": res.data.display_name});

        this.$router.push('/')
      }).catch(error => {
        this.$notify.error({
          title: '错误',
          message: error.data.msg.detail
        });
      });
    }
  }
}
</script>

<style scoped lang="scss">
.main-container {
  text-align: center;
  position: absolute;
  top: 30%;
  left: 50%;
  transform: translate(-50%, -30%);
  background-color: #FFFFFF;
  border: #FFFFFF solid 1px;
  width: 380px;
  height: 320px;
  border-radius: 5px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);

  .form {
    box-sizing: border-box;
    width: 100%;
    height: 100%;
    padding: 0 60px;

    .title {
      margin-top: 30px;
      font-size: 24px;
      font-style: normal;
      color: #606266;
      margin-bottom: 30px;
    }

    .input {
      width: 100%;
      height: 100%;

      .el-button {
        width: 260px;
      }
    }
  }
}
</style>
