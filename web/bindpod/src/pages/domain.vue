<template>
  <div class="domain">
    <el-container v-if="$route.name === 'domain'">
      <el-row class="content">
        <el-col>
            <div class="abstract">
              <el-row type="flex" justify="space-between">
                <el-col :span="4" :push="1">
                  <div class="displayData">
                    <div class="text">
                      <div><i class="el-icon-s-release"></i></div>
                      <div><span>{{statisticsData.domain_total}}</span></div>
                      <div><p>域名总数</p></div>
                    </div>
                  </div>
                </el-col>
                <el-col :span="4">
                  <div class="displayData">
                    <div class="text">
                      <div><i class="el-icon-s-release"></i></div>
                      <div><span>{{ statisticsData.analysis_active_total }}</span></div>
                      <div><p>已解析数量</p></div>
                    </div>
                  </div>
                </el-col>
                <el-col :span="4" :pull="1">
                  <div class="displayData">
                    <div class="text">
                      <div><i class="el-icon-s-release"></i></div>
                      <div><span>{{ statisticsData.analysis_stop_total }}</span></div>
                      <div><p>暂停解析数量</p></div>
                    </div>
                  </div>
                </el-col>
              </el-row>
            </div>
        </el-col>
        <el-col class="tables">
          <el-row>
            <el-col>
              <div class="domainBtn">
                <el-form :inline="true">
                  <el-form-item><el-button size="medium" plain @click="dialogFormVisible = true">添加域名</el-button></el-form-item>
                  <el-form-item><el-button size="medium" plain @click="submitDelete">删除域名</el-button></el-form-item>
                  <el-form-item><el-input placeholder="请输入搜索内容" clearable size="medium" prefix-icon="el-icon-search" v-model="pagination.search"
                                          @input="searchDomain"></el-input></el-form-item>
                </el-form>
              </div>
            </el-col>
            <el-col>
              <div class="data">
                <el-table ref="multipleTable" :data="pagination.domainList" size="medium" v-loading="loading" @selection-change="tableSelection" width="100%">
                  <el-table-column header-align="center" align="center"
                                   type="selection"
                                   width="55">
                  </el-table-column>
                  <el-table-column
                      label="域名" prop="domain" show-overflow-tooltip header-align="center" align="center">
                  </el-table-column>
                  <el-table-column
                      label="区域文件位置" prop="path" show-overflow-tooltip header-align="center" align="center">
                  </el-table-column>
                  <el-table-column
                      label="解析数量" prop="analysis" header-align="center" align="center">
                  </el-table-column>
                  <el-table-column label="创建时间" header-align="center" align="center">
                    <template slot-scope="scope">
                      <i class="el-icon-time"></i>
                      <span style="margin-left: 10px">{{ scope.row.create_time }}</span>
                    </template>
                  </el-table-column>
                  <el-table-column label="操作" header-align="center" align="center">
                    <template slot-scope="scope">
                      <el-button
                          size="mini" @click="analysisHandle(scope.row)">解析
                      </el-button>
                    </template>
                  </el-table-column>
                </el-table>
                <div class="page block" v-show="!loading" :current-page.sync="pagination.current">
                  <el-pagination
                      background
                      :page-size="pagination.size"
                      layout="total, prev, pager, next, jumper"
                      :total="pagination.total" v-show="pagination.total!==0" @current-change="pageDown">
                  </el-pagination>
                </div>
              </div>
            </el-col>
          </el-row>
        </el-col>
        <el-col>
          <el-dialog
              title="添加域名"
              :visible.sync="dialogFormVisible"
              width="380px"
              :modal-append-to-body='false' @closed="clearDialog">
            <el-form :model="form" status-icon :rules="rules" ref="form" size="small">
              <el-form-item label="顶级域名" label-width="100px" prop="domain">
                <el-input v-model="form.domain" autocomplete="off" clearable size="small"></el-input>
              </el-form-item>
              <el-form-item label="区域文件路径" label-width="100px" prop="path">
                <el-input v-model="form.path" autocomplete="off" clearable size="small"></el-input>
              </el-form-item>
            </el-form>
            <span slot="footer" class="dialog-footer">
              <el-button @click="dialogFormVisible = false" size="small">取 消</el-button>
              <el-button type="primary" @click="addDomain" size="small">确 定</el-button>
            </span>
          </el-dialog>
        </el-col>
      </el-row>
    </el-container>
    <router-view></router-view>
  </div>
</template>

<script>
export default {
  name: "domain",
  mounted() {
    this.axios.all([this.getDomainList(), this.statistics()]);
  },
  methods: {
    analysisHandle(value) {
      this.$router.push({
        name: 'analysis',
        params: {
          domain: value.domain,
        }
      });
    },
    addDomain() {
      if(this.form.domain.trim() === '' || this.form.path.trim() === '') {
        this.$refs.form.validateField('domain');
        this.$refs.form.validateField('path');
        return false;
      }
      this.axios.post("/agent/domain/create/", {
        domain: this.form.domain,
        path: this.form.path
      }, {
        headers: {
          'Authorization': this.$cookie.get('token')
        }
      }).then(res =>{
        if (res.data.code !== 200) {
          this.tools.notify(res.data.msg, "提示", "error");
          return false;
        }
        this.tools.notify(res.data.msg, "提示", "success");
        this.axios.all([this.getDomainList(), this.statistics()]);
        this.dialogFormVisible = false;
      });
    },
    tableSelection(val) {
      this.selectDelete.splice(0, this.selectDelete.length);
      val.forEach((value) => {
        this.selectDelete.push(value.domain)
      });
    },
    clearDialog() {
      for (let key in this.form) {
        this.form[key] = '';
      }
      this.$refs.form.resetFields('username');
      this.$refs.form.resetFields('path');
    },
    submitDelete() {
      if (this.selectDelete.length === 0) {
        this.tools.notify("选择要删除的域名", "提示", "warning");
        return false;
      }
      this.$confirm('确定删除选中的域名?', '删除', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
        center: true
      }).then(() => {
        this.axios.post("/agent/domain/delete/", {
          domain: this.selectDelete
        }, {
          headers: {
            'Authorization': this.$cookie.get('token')
          }
        }).then(res =>{
          let msgType = 'success';
          if (res.data.code !== 200) {
            msgType = 'error';
          }
          this.tools.notify(res.data.msg, "提示", msgType)
          this.axios.all([this.getDomainList(), this.statistics()]);
        });
      });
    },
    searchDomain() {
      this.pagination.current = 1;
      this.getDomainList();
    },
    pageDown(page) {
      this.pagination.current = page;
      this.getDomainList();
    },
    getDomainList() {
      let url = `/agent/domain/?size=${this.pagination.size}&page=${this.pagination.current}&domain=${this.pagination.search}`;
      this.axios.get(url, {
        headers: {
          'Authorization': this.$cookie.get('token')
        }
      }).then(res => {
        this.pagination.domainList = res.data.data.data;
        this.pagination.total = res.data.data.page_num.count;
      });

    },
    statistics() {
      this.axios.get("/agent/domain/info/", {
        headers: {
          'Authorization': this.$cookie.get('token')
        }
      }).then(res => {
        this.statisticsData.domain_total = res.data.data.domain_total
        this.statisticsData.analysis_active_total = res.data.data.analysis_active_total
        this.statisticsData.analysis_stop_total = res.data.data.analysis_stop_total
      });
    },
  },
  data() {
    let checkDomain = (rule, value, callback) => {
        if (value === ''){
          switch (rule.field){
            case 'domain':
              callback(new Error('域名不能为空'));
              break;
            case 'path':
              callback(new Error('区域文件路径不能为空'));
              break;
         }
        }
        callback();
    };
    return {
      statisticsData: {
        domain_total: 0,
        analysis_active_total:0,
        analysis_stop_total: 0
      },
      pagination: {
        current: 1,
        total: 0,
        size: 10,
        search: '',
        domainList: [],
      },
      form: {
        domain: '',
        path: '',
      },
      rules: {
        domain: [{validator: checkDomain, trigger: 'blur'}],
        path: [{validator: checkDomain, trigger: 'blur'}],
      },
      selectDelete: [],
      dialogFormVisible: false,
      loading: false,
    }
  },
}
</script>

<style scoped lang="scss">
.domain {
  width: 100%;
  height: 100%;
  .content {
    width: 100%;
    .abstract {
      background-color: #F5F7FA;
      height: 100%;
      padding-bottom: 10px;
      .displayData {
        position: relative;
        top: 50%;
        transform: translateY(-50%);
        background-color: #FFFFFF;
        width: 230px;
        height: 80px;
        border: 1px solid #FFFFFF;
        border-radius: 4px;
        color: #303133;
        font-size: 14px;
        font-weight: 3;
        text-align: center;
        line-height: 20px;
        .text {
          position: absolute;
          top: 50%;
          left: 50%;
          transform: translate(-50%, -50%);
        }
      }
    }
    .tables {
      background-color: #FFFFFF;
      .domainBtn {
        display: flex;
        justify-content: flex-start;
        margin-top: 20px;
        margin-left: 50px;
      }
      .data {
        width: 90%;
        margin-left: 48px;
        margin-bottom: 20px;
        .page {
          width: 100%;
          text-align: center;
          margin-top: 15px;
        }
      }
    }
  }
}
</style>
