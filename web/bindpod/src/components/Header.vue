<template>
  <div id="header">
    <el-dialog title="修改密码" :visible.sync="dialogFormVisible" width="20%" @closed="changeCancel">
      <el-form :model="form">
        <el-form-item label="新密码" :label-width="formLabelWidth">
          <el-input show-password v-model="form.Password" autocomplete="off"></el-input>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogFormVisible = false">取 消</el-button>
        <el-button type="primary" @click="changeSubmit">确 定</el-button>
      </div>
    </el-dialog>
    <el-header>
      <el-container>
        <div class="logo">
          BindPod
        </div>
        <div class="userInfo">
          <el-dropdown @command="handleCommand">
            <span class="el-dropdown-link">
              {{ username }}<i class="el-icon-arrow-down el-icon--right"></i>
            </span>
            <el-dropdown-menu slot="dropdown">
              <el-dropdown-item command="changePassword"><i class="el-icon-user"></i>修改密码</el-dropdown-item>
              <el-dropdown-item command="logout"><i class="el-icon-s-promotion"></i>安全退出</el-dropdown-item>
            </el-dropdown-menu>
          </el-dropdown>
        </div>
      </el-container>
    </el-header>
  </div>
</template>

<script>
export default {
  name: "Header",
  computed: {
    username(){
      return this.$cookie.get("username", "")
    }
  },
  data() {
    return {
      dialogFormVisible: false,
      formLabelWidth: '60px',
      form: {
        Password: ''
      },

    }
  },
  methods: {
    changeSubmit() {
      let username = this.$cookie.get('user');
      let password = this.form.Password;
      this.axios.post('/agent/user/change/', {
        password,
        username
      }, {
        headers: {
          'Authorization': this.$cookie.get('Token')
        }
      }).then(res => {
        let msgType = 'success';
        if (res.data.code !== 200) {
          msgType = 'error';
        }
        this.$message({
          message: res.data.msg,
          type: msgType,
        });
        this.dialogFormVisible = false;
        this.$cookie.delete('Token');
        this.$cookie.delete('username');
        this.$cookie.delete('user');
        this.$cookie.delete('is_superuser');
        this.$router.push('/login');
      });
    },
    changeCancel() {
      this.form =  {
        Password: ''
      }
    },
    handleCommand(command) {
      if (command === 'logout') {
        this.$confirm('确定退出当前账号？', '退出', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning',
          center: true
        }).then(() => {
          let username = this.$cookie.get('user');
          this.axios.post('/logout/', {
            username,
          }, {
            headers: {
              'Authorization': this.$cookie.get('Token')
            }
          });
          this.$cookie.delete('Token');
          this.$cookie.delete('username');
          this.$cookie.delete('user');
          this.$cookie.delete('is_superuser');
          this.$router.push('/login');
        });
      } else {
        this.dialogFormVisible = true;
      }
    }
  }
}
</script>

<style lang="scss" scoped>

#menu {
  .el-header {
    background-color: #409EFF;
    line-height: 60px;

    .el-container {
      justify-content: space-between;
    }

    .el-dropdown-link {
      color: #FFFFFF;
    }
  }
}

</style>