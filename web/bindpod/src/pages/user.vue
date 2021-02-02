<template>
  <div class="user">
    <el-container>
      <el-row>
        <el-col>
          <div class="searchDiv">
            <el-form :inline="true">
              <el-form-item>
                <el-button size="medium" plain @click="showAddUser">添加用户</el-button>
              </el-form-item>
              <el-form-item>
                <el-button size="medium" plain @click="deleteUser">删除用户</el-button>
              </el-form-item>
              <el-form-item>
                <el-input size="medium" prefix-icon="el-icon-search" placeholder="搜索用户" v-model="pagination.search" @input="getUserList"></el-input>
              </el-form-item>
            </el-form>
          </div>
        </el-col>
        <el-col>
          <div class="data">
            <div class="tableDialog">
              <el-dialog :title="UserDialogTitle" :visible.sync="UserDialog" :modal-append-to-body='false' width="450px"
                         @closed="clearDialog">
                <el-form :model="form" status-icon :rules="rules" ref="form" :inline="true" size="small">
                  <el-form-item prop="username">
                    <el-input v-model="form.username" :disabled="!form.usernameDisable" placeholder="用户名" size="small"
                              clearable></el-input>
                  </el-form-item>
                  <el-form-item prop="firstname">
                    <el-input v-model="form.firstname" placeholder="姓名" size="small" clearable></el-input>
                  </el-form-item>
                  <el-form-item prop="email">
                    <el-input v-model="form.email" placeholder="邮箱" size="small" clearable></el-input>
                  </el-form-item>
                  <el-form-item prop="password">
                    <el-input v-model="form.password" placeholder="密码" show-password clearable size="small"></el-input>
                  </el-form-item>
                  <el-form-item>
                    <el-checkbox v-model="form.userActive" border label="激活" size="small"></el-checkbox>
                  </el-form-item>
                  <el-form-item>
                    <el-checkbox border v-model="form.userSupper" label="管理员" size="small"></el-checkbox>
                  </el-form-item>
                </el-form>
                <span slot="footer" class="dialog-footer">
                  <el-button @click="UserDialog = false" size="small">取 消</el-button>
                  <el-button type="primary" @click="UserInfoSubmit" size="small">确 定</el-button>
                </span>
              </el-dialog>
            </div>
            <div class="drawer-left">
              <el-drawer
                  :visible.sync="domainData.drawer"
                  direction="rtl" :destroyOnClose="true"
                  size="600px" :modal-append-to-body='false' :with-header="false" @open="drawerOpen"
                  @closed="drawerClose">
                <el-row>
                  <el-col>
                    <div style="width: 500px; margin-left: 50px; margin-top: 50px">
                      <el-col>
                        <el-input placeholder="搜索域名" @input="drawerOpen" v-model="domainData.search"
                                  prefix-icon="el-icon-search"></el-input>
                      </el-col>
                      <el-table ref="multipleTable" size="medium" v-loading="domainData.loading"
                                :data="domainData.domainList"
                                style="width: 100%" @selection-change="tableSelection" height="704px">
                        <el-table-column
                            label="域名" prop="domain" show-overflow-tooltip header-align="center" align="center"
                            width="420px">
                        </el-table-column>
                        <el-table-column label="授权" header-align="center" align="center" width="80px">
                          <template slot-scope="scope">
                            <el-switch
                                v-model="scope.row.status" active-color="#13ce66" inactive-color="#ff4949"
                                @change="userBindDomain($event, scope.row)">
                            </el-switch>
                          </template>
                        </el-table-column>
                      </el-table>
                      <div class="page block" v-show="!domainData.loading" :current-page.sync="domainData.current">
                        <el-pagination
                            background
                            :page-size="domainData.size"
                            layout="total, prev, pager, next, jumper"
                            :total="domainData.total" v-show="domainData.total!==0" @current-change="drawerPageDown">
                        </el-pagination>
                      </div>
                    </div>
                  </el-col>
                </el-row>
              </el-drawer>
            </div>
            <el-table ref="multipleTable" size="medium" v-loading="loading" :data="tableData"
                      style="width: 100%" @selection-change="tableSelection">
              <el-table-column header-align="center" align="center"
                               type="selection"
                               width="55">
              </el-table-column>
              <el-table-column
                  label="账号" prop="username" show-overflow-tooltip header-align="center" align="center" width="100px">
              </el-table-column>
              <el-table-column
                  label="姓名" prop="first_name" header-align="center" align="center" width="100px">
              </el-table-column>
              <el-table-column label="邮箱" prop="email" header-align="center" align="center">
              </el-table-column>
              <el-table-column label="状态" header-align="center" align="center" width="80px">
                <template slot-scope="scope">
                  <el-switch
                      v-model="scope.row.is_active" active-color="#13ce66" inactive-color="#ff4949"
                      @change="changeActive($event, scope.row)">
                  </el-switch>
                </template>
              </el-table-column>
              <el-table-column label="管理员" header-align="center" align="center" width="80px">
                <template slot-scope="scope">
                  <el-tag
                      :type="scope.row.is_superuser ? 'success' : 'danger'" size="small"
                      disable-transitions>{{ scope.row.is_superuser ? '是' : '否' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column
                  label="时间" show-overflow-tooltip header-align="center" align="center">
                <template slot-scope="scope">
                  <i class="el-icon-time"></i>
                  <span style="margin-left: 10px">{{ scope.row.create_time }}</span>
                </template>
              </el-table-column>
              <el-table-column label="操作" header-align="center" align="center">
                <template slot-scope="scope">
                  <el-button
                      size="mini"
                      @click="bindDomain(scope.row)" :disabled="!is_superuser">授权域名
                  </el-button>
                  <el-button
                      size="mini" plain
                      @click="changeUserInfo(scope.row)">用户信息修改
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
          <div class="page block" v-show="!loading" :current-page.sync="pagination.current">
            <el-pagination
                background
                :page-size="pagination.size"
                layout="total, prev, pager, next, jumper"
                :total="pagination.total" v-show="pagination.total!==0" @current-change="pageDown">
            </el-pagination>
          </div>
        </el-col>
      </el-row>
    </el-container>
  </div>
</template>

<script>
import {mapState} from "vuex";

export default {
  name: "user",
  data() {
    let checkExists = (rule, value, callback) => {
      if (value === '') {
        switch (rule.field) {
          case 'username':
            callback(new Error('用户名不能为空'));
            break;
          case 'firstname':
            callback(new Error('姓名不能为空'));
            break;
          case 'email':
            callback(new Error('邮箱不能为空'));
            break;
          case 'password':
            callback(new Error('密码不能空'));
            break;
        }
      }
      callback();
    };

    return {
      domainData: {
        drawer: false,
        loading: false,
        bindUser: '',
        domainList: [],
        search: '',
        current: 1,
        total: 0,
        size: 15,
      },
      form: {
        usernameDisable: true,
        username: '',
        password: '',
        firstname: '',
        email: '',
        userActive: true,
        userSupper: false
      },
      rules: {
        username: [{validator: checkExists, trigger: 'blur'}],
        password: [{validator: checkExists, trigger: 'blur'}],
        firstname: [{validator: checkExists, trigger: 'blur'}],
        email: [{validator: checkExists, trigger: 'blur'}],
      },
      UserDialogTitle: '创建用户',
      UserDialog: false,
      loading: false,
      tableData: [],
      selectDelete: [],
      pagination: {
        search: '',
        current: 1,
        total: 0,
        size: 10,
      },
    }
  },
  methods: {
    userBindDomain(status, value) {
      let url = "/agent/user/add/remove/"
      if (status) {
        url = "/agent/user/add/domain/"
      }
      this.axios.post(url, {
        username: this.domainData.bindUser,
        domain: value.domain,
      }, {
        headers: {
          'Authorization': this.$cookie.get('token')
        }
      }).then(res => {
        let msgType = 'success';
        if (res.data.code !== 200) {
          msgType = 'error';
        }
        this.tools.notify(res.data.msg, "提示", msgType, "top-left");
        this.drawerOpen();
      }).catch(() => {
        this.tools.notify("授权域名失败", "提示", "error", "top-left");
      });
    },
    drawerPageDown(page) {
      this.domainData.current = page;
      this.drawerOpen();
    },
    drawerOpen() {
      this.domainData.loading = true;
      let url = `/agent/user/domain/${this.domainData.bindUser}/?size=${this.domainData.size}&page=${this.domainData.current}&search=${this.domainData.search}`
      this.axios.get(url, {
        headers: {
          'Authorization': this.$cookie.get('token')
        }
      }).then(res => {
        this.domainData.domainList = res.data.data.data
        this.domainData.total = res.data.data.page_num.count
      }).catch(() => {
        this.tools.notify("加载数据失败", "错误", "error");
      });
      this.domainData.loading = false;
    },
    drawerClose() {
      this.domainData = {
        drawer: false,
        loading: false,
        bindUser: '',
        domainList: [],
        search: '',
        current: 1,
        total: 0,
        size: 10,
      }
    },
    bindDomain(value) {
      this.domainData.bindUser = value.username;
      this.domainData.drawer = true;
    },
    changeUserInfo(data) {
      this.form.userActive = data["is_active"];
      this.form.userSupper = data["is_superuser"];
      this.form.username = data["username"];
      this.form.firstname = data["first_name"];
      this.form.email = data["email"];
      this.UserDialogTitle = "修改用户信息";
      this.UserDialog = true;
      this.form.usernameDisable = false;
    },
    clearDialog() {
      this.form = {
        usernameDisable: true,
        username: '',
        password: '',
        firstname: '',
        email: '',
        userActive: true,
        userSupper: false
      }
      this.$refs.form.resetFields('username');
      this.$refs.form.resetFields('firstname');
      this.$refs.form.resetFields('email');
      this.$refs.form.resetFields('password');
    },
    showAddUser() {
      this.UserDialogTitle = '添加用户'
      this.UserDialog = true
    },
    handAddUser() {
      let {username, firstname, email, password, userActive, userSupper} = this.form
      if (username === '' || firstname === '' || email === '' || password === '') {
        this.$refs.form.validateField('username');
        this.$refs.form.validateField('firstname');
        this.$refs.form.validateField('email');
        this.$refs.form.validateField('password');
        return false;
      }
      let data = {
        username: username,
        first_name: firstname,
        email: email,
        password: password,
        is_active: userActive,
        is_superuser: userSupper,

      }
      this.axios.post('/agent/user/create/', data, {
        headers: {
          'Authorization': this.$cookie.get('token')
        }
      }).then((res) => {
        let msgType = 'success';
        if (res.data.code !== 200) {
          msgType = 'error';
        }
        this.tools.notify(res.data.msg, "提示", msgType);
        this.pagination.current = 1;
        this.getUserList();
      }).catch(() => {
        this.tools.notify("添加用户失败", "提示", "error");
      });
      this.UserDialog = false;
    },
    handleEditUserInfo() {
      let {username, firstname, email, password, userActive, userSupper} = this.form
      let data = {
        username: username,
        first_name: firstname,
        email: email,
        is_active: userActive,
        is_superuser: userSupper
      }
      if (password.trim().length !== 0) {
        data["password"] = password;
      }
      this.axios.post('/agent/user/password/', data, {
        headers: {
          'Authorization': this.$cookie.get('token')
        }
      }).then(res => {
        let msgType = 'success';
        if (res.data.code !== 200) {
          msgType = 'error';
        }
        this.tools.notify(res.data.msg, "提示", msgType);
        this.getUserList();
      }).catch(() => {
        this.tools.notify("修改用户信息失败", "提示", "error");
      });
      this.UserDialog = false;
    },
    UserInfoSubmit() {
      if (this.UserDialogTitle !== '修改用户信息') {
        this.handAddUser();
      } else {
        this.handleEditUserInfo();
      }
    },
    changeActive(event, value) {
      this.axios.post('/agent/user/active/', {
        username: value.username,
        active: event,
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
      }).catch(() => {
        this.tools.notify("用户禁用失败", "提示", "error");
      });
    },
    deleteUser() {
      if (this.selectDelete.length === 0) {
        this.tools.notify("选择要删除的用户", "提示", "warning");
        return false;
      }
      this.$confirm('确定删除选中的用户?', '删除', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
        center: true
      }).then(() => {
        this.axios.post("/agent/user/delete/", {
          username: this.selectDelete
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
          this.pagination.current = 1;
          this.getUserList();
        }).catch(() => {
          this.tools.notify("山用户失败", "提示", "error");
        });
      });
    },
    tableSelection(val) {
      this.selectDelete.splice(0, this.selectDelete.length);
      val.forEach((value) => {
        this.selectDelete.push(value.username)
      });
    },
    pageDown(page) {
      this.pagination.current = page;
      this.getUserList();
    },
    getUserList() {
      this.loading = true;
      let url = `/agent/user/?size=${this.pagination.size}&page=${this.pagination.current}&username=${this.pagination.search}`;
      this.axios.get(url, {
        headers: {
          'Authorization': this.$cookie.get('token')
        }
      }).then(res => {
        this.pagination.total = res.data.data.page_num.count;
        this.tableData = res.data.data.data;
      }).catch(() => {
        this.tools.notify("加载数据失败", "错误", "error");
      });
      this.loading = false;
    }
  },
  computed: {
    ...mapState(['is_superuser']),
  },
  mounted() {
    this.getUserList();
  }
}
</script>

<style scoped lang="scss">
.user {
  margin: 0 10px 10px 0;
  height: 100%;
  width: 100%;

  .searchDiv {
    margin-top: 50px;
    margin-left: 50px;
  }

  .data {
    width: 90%;
    margin-left: 48px;
    margin-bottom: 20px;
  }

  .page {
    width: 100%;
    text-align: center;
    margin-top: 15px;
  }
}
</style>
