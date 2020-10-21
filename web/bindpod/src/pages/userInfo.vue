<template>
  <div class="user">
    <el-dialog title="添加用户" :visible.sync="dialogFormVisible" width="20%" center @closed="closeDialog">
      <el-form :model="form" class="dialogForm">
        <el-form-item label="用户名" :label-width="formLabelWidth">
          <el-input @blur="checkInputValue" placeholder="请填写内容" size="medium" v-model="form.username"
                    autocomplete="off"></el-input>
        </el-form-item>
        <el-form-item label="姓名" :label-width="formLabelWidth">
          <el-input placeholder="请填写内容" @blur="checkInputValue" size="medium" v-model="form.first_name"
                    autocomplete="off"></el-input>
        </el-form-item>
        <el-form-item label="" :label-width="formLabelWidth">
          <el-checkbox v-model="form.is_superuser" label="禁用">是否是管理员</el-checkbox>
        </el-form-item>
        <el-form-item label="密码" :label-width="formLabelWidth">
          <el-input placeholder="请填写内容" @blur="checkInputValue" size="medium" v-model="form.password"
                    autocomplete="off"></el-input>
        </el-form-item>
        <el-form-item label="邮箱" :label-width="formLabelWidth">
          <el-input placeholder="请填写内容" @blur="checkInputValue" size="medium" v-model="form.email"
                    autocomplete="off"></el-input>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button size="medium" @click="dialogFormVisible = false">取 消</el-button>
        <el-button size="medium" type="primary" @click="submit">确 定</el-button>
      </div>
    </el-dialog>
    <el-dialog title="授权域名" :visible.sync="dialogTDomainAbleVisible" width="30%">
      <el-table :data="authDomainList.domain" style="width: 100%;">
        <el-table-column prop="domain" label="域名"></el-table-column>
        <el-table-column
            label="是否授权">
          <template slot-scope="scope">
            <el-switch
                v-model="scope.row.status" inactive-color="#ff4949" @change="userDomainChange($event, scope.row)">
            </el-switch>
          </template>
        </el-table-column>
      </el-table>
      <div class="block">
        <el-pagination
            layout="prev, pager, next"
            :total="domainTotal" :page-size="domainSize" @current-change="getUserDomain">
        </el-pagination>
      </div>
    </el-dialog>
    <BaseTemplate router-name="用户管理" router-path="/user">
      <template v-slot:main>
        <div class="userMain">
          <div class="table">
            <div class="search">
              <div>
                <el-button size="medium" type="primary" @click="dialogFormVisible = true"><i class="el-icon-plus"></i>&nbsp;添加
                </el-button>
                <el-button size="medium" type="danger" @click="delUser"><i class="el-icon-delete"></i>&nbsp;删除
                </el-button>
              </div>
              <div>
                <el-input size="medium" suffix-icon="el-icon-search" v-model="search" placeholder="请输入用户名"
                          @input="searchUser"></el-input>
              </div>
            </div>
            <el-table
                :data="tableData"
                style="width: 100%" @selection-change="handleSelectionChange">
              <el-table-column type="selection" width="55">
              </el-table-column>
              <el-table-column
                  label="账号">
                <template slot-scope="scope">
                  <span style="margin-left: 10px">{{ scope.row.username }}</span>
                </template>
              </el-table-column>
              <el-table-column
                  label="姓名">
                <template slot-scope="scope">
                  <span style="margin-left: 10px">{{ scope.row.first_name }}</span>
                </template>
              </el-table-column>
              <el-table-column
                  label="邮箱">
                <template slot-scope="scope">
                  <span style="margin-left: 10px">{{ scope.row.email }}</span>
                </template>
              </el-table-column>
              <el-table-column
                  label="状态" width="120px">
                <template slot-scope="scope">
                  <el-switch
                      v-model="scope.row.is_active" inactive-color="#ff4949" @change="changeActive($event, scope.row)">
                  </el-switch>
                </template>
              </el-table-column>
              <el-table-column
                  label="管理员" width="100px">
                <template slot-scope="scope">
                  <div style="width: 30px; height: 20px; margin-left: 15px">
                    <span class="el-icon-circle-check" v-if="scope.row.is_superuser"
                          style="color: #67C23A;font-size: 18px"></span>
                    <span class="el-icon-circle-close" v-else style="color: #F56C6C;font-size: 18px"></span>
                  </div>
                </template>
              </el-table-column>
              <el-table-column
                  label="创建时间" width="110px">
                <template slot-scope="scope">
                  <span style="margin-left: 10px">{{ scope.row.create_time }}</span>
                </template>
              </el-table-column>
              <el-table-column label="操作">
                <template slot-scope="scope">
                  <el-button
                      size="mini"
                      @click="authDomain(scope.row)" v-if="!scope.row.is_superuser">授权域名
                  </el-button >
                  <el-button
                      size="mini"
                      type="primary"
                      @click="changePassword(scope.row)">修改密码
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
          <div class="block">
            <el-pagination
                layout="prev, pager, next"
                :total="userTotal" :page-size="pageSize" :current-page="page" @current-change="init">
            </el-pagination>
          </div>
        </div>
      </template>
    </BaseTemplate>
  </div>
</template>

<script>
import BaseTemplate from "@/components/BaseTemplate";

export default {
  name: "user",
  data() {
    return {
      search: '',
      deleteUser: [],
      dialogFormVisible: false,
      formLabelWidth: '70px',
      dialogTDomainAbleVisible: false,
      authDomainList: {},
      domainTotal: 0,
      domainSize: 5,
      page: 1,
      userTotal: 0,
      pageSize: 10,
      domainPage: 1,
      form: {
        username: '',
        first_name: '',
        password: '',
        email: '',
        is_superuser: false,
      },
      tableData: []
    }
  },
  methods: {
    userDomainChange(status, value){
      let url = "/agent/user/add/remove/"
      if(status){
        url = "/agent/user/add/domain/"
      }
      this.axios.post(url, {
        username: this.authDomainList.username,
        domain: value.domain,
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
        })
      });

    },
    changeActive(status, value) {
      this.axios.post('/agent/user/active/', {
        username: value.username,
        active: status,
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
        })
      });
    },
    getUserDomain(page) {
      console.log(page)
      this.domainPage = page;
      this.axios.get('/agent/user/domain/'+this.authDomainList.username+'/?size=5&page='+this.domainPage, {
        headers: {
          'Authorization': this.$cookie.get('Token')
        }
      }).then(res => {
        this.authDomainList = {
          domain: res.data.data.data,
          username: this.authDomainList.username
        }
        this.domainTotal = res.data.data.page_num.count
      });
    },
    authDomain(row) {
      this.authDomainList.username = row.username.toString();
      this.getUserDomain(1);
      this.dialogTDomainAbleVisible = true;
    },
    changePassword(row) {
      this.$prompt('请输入新密码', '修改密码', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        inputType: 'password',
      }).then(({value}) => {
        this.axios.post('/agent/user/password/', {
          username: row.username.toString(),
          password: value
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
          })
        });
      });
    },
    submit() {
      for (let k in this.form) {
        if (k === 'is_superuser') {
          continue;
        }
        if (k.trim() === 'email') {
          if (this.form[k].trim().split('@').length !== 2) {
            this.$message({
              message: '请填写正确的邮箱格式!',
              type: 'error'
            })
            return;
          }
        }
        if (this.form[k].trim().length === 0) {
          this.$message({
            message: '表单没有填写完成!',
            type: 'error'
          })
          return;
        }
      }
      this.axios.post('/agent/user/create/', this.form, {
        headers: {
          'Authorization': this.$cookie.get('Token')
        }
      }).then((res) => {
        let msgType = 'success';
        if (res.data.code !== 200) {
          msgType = 'error';
        }
        this.$message({
          message: res.data.msg,
          type: msgType,
        })
        this.init(this.page);
      })
      this.dialogFormVisible = false;
    },

    checkInputValue(event) {
      if (event.target.value.trim().length === 0) {
        event.target.placeholder = "请填写内容";
      }
    },
    closeDialog() {
      this.form = {
        username: '',
        is_superuser: false,
        first_name: '',
        password: '',
        email: ''
      }
    },
    delUser() {
      if (this.deleteUser.length === 0) {
        this.$message({
          message: '未选择用户',
          type: 'warning'
        })
        return
      }
      this.axios.post('/agent/user/delete/', {
        username: this.deleteUser
      }, {
        headers: {
          'Authorization': this.$cookie.get('Token')
        }
      }).then((res) => {
        let msgType = 'success';
        if (res.data.code !== 200) {
          msgType = 'error';
        }
        this.$message({
          message: res.data.msg,
          type: msgType,
        })
        this.init(this.page);
      })
    },
    searchUser() {
      this.init(this.page)
    },
    handleSelectionChange(selection) {
      this.deleteUser = [];
      selection.filter((value) => {
        this.deleteUser.push(value.username.toString())
      })
    },
    init(page) {
      this.page = page
      this.axios.get("/agent/user/?size=10&page=" + this.page + "&username=" + this.search, {
        headers: {
          'Authorization': this.$cookie.get('Token')
        }
      }).then(res => {
        this.userTotal = res.data.data.page_num.count;
        this.tableData = res.data.data.data;
      });
    },
  },
  components: {BaseTemplate},
  mounted() {
    this.init(this.page);
  }
}
</script>

<style lang="scss" scoped>
.userMain {
  border-radius: 5px;
  width: 100%;
  height: 100%;
  background-color: #FFFFFF;

  .table {
    padding: 0 20px;
    width: 100%;
    margin-top: 10px;
    background-color: #FFFFFF;
    border: 1px solid #FFFFFF;
    border-radius: 5px;

    .search {
      display: flex;
      margin: 30px 50px 20px;

      div {
        margin-right: 30px;
      }
    }

    .block {
      margin: 15px 0 100px;
    }
  }

}
</style>