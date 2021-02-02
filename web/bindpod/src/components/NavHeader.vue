<template>
  <div class="nav-header">
      <el-row type="flex" class="row" justify="space-between">
        <el-col :span="12">
          <div class="logo">BindPod</div>
        </el-col>
        <el-col :span="12">
          <div class="user">
            <el-dropdown @command="handleCommand">
                <span class="el-dropdown-link">
                  <span>{{ display_name.trim() === '' ? username : display_name }}</span>
                  <i class="el-icon-arrow-down el-icon--right"></i>
                </span>
              <modal :btn-type="true" title="修改密码" :show-modal="showModal" @cancel="closeChangePassword"
                     @submit="changePassword">
                <template v-slot:body>
                  <el-form :model="form" :rules="rules" ref="form">
                    <el-form-item prop="password">
                      <el-input style="width: 300px" size="medium" v-model="form.password" show-password placeholder="输入新密码"></el-input>
                    </el-form-item>
                  </el-form>
                </template>
              </modal>
              <el-dropdown-menu slot="dropdown">
                <el-dropdown-item command="1"><i class="el-icon-user"></i>修改密码</el-dropdown-item>
                <el-dropdown-item command="2"><i class="el-icon-s-promotion"></i>安全退出</el-dropdown-item>
              </el-dropdown-menu>
            </el-dropdown>
          </div>
        </el-col>
      </el-row>
  </div>
</template>

<script>
import Modal from "@/components/Modal";
import {mapState} from "vuex";

export default {
  name: "NavHeader",
  data() {
    return {
      form: {
        password: '',
      },
      showModal: false,
      rules: {
        password: [{
          required: true, message: '旧密码不能为空', trigger: 'blur'
        }],
      },
    }
  },
  methods: {
    logout() {
      this.$cookie.delete("userinfo");
      this.$cookie.delete("token");
      this.$router.push('/login');
    },
    handleCommand(command) {
      if (command === "1") {
        this.showModal = true;
      } else if (command === "2") {
        this.logout();
      }
    },
    closeChangePassword() {
      this.showModal = false;
      this.form.oldPassword = "";
      this.form.newPassword = "";
      this.$refs.form.resetFields('password');
    },
    changePassword() {
      if (this.form.password.trim().length ===0){
        this.$refs.form.validateField('password');
        return false;
      }
      let username = this.username;
      let password = this.form.password;
      this.axios.post('/agent/user/change/', {
        password,
        username
      }, {
        headers: {
          'Authorization': this.$cookie.get('token')
        }
      }).then(res => {
        let msgType = 'success';
        if (res.data.code !== 200) {
          msgType = 'error';
        }
        this.tools.notify(res.data.msg, "提示", msgType);
        this.logout();
      }).catch(()=>{
        this.tools.notify("密码修改失败", "提示", "error");
      });
    },
  },
  computed: {
    ...mapState(['username', 'display_name', 'type']),
  },
  components: {Modal}
}
</script>

<style scoped lang="scss">
.nav-header {
  background-color: #409EFF;
  width: 100%;
  height: 100%;
  line-height: 60px;
  .row {
    position: relative;
    height: 100%;
    width: 100%;
    .logo {
      color: #FFFFFF;
      font-size: 18px;
      font-weight: 400;
      height: 100%;
      position: absolute;
      left: 0;
    }
    .user {
      position: absolute;
      right: 0;
      .el-dropdown-link {
        color: #FFFFFF;
        font-size: 16px;
      }
    }

  }
}
</style>
