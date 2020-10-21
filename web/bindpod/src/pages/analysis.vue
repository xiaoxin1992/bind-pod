<template>
  <div class="analysis">
    <el-dialog :title="dialogTitle" :visible.sync="dialogFormVisible" width="20%" center @closed="closeDialog">
      <el-form :model="form" class="dialogForm">
        <el-form-item label="名称" :label-width="formLabelWidth">
          <el-input @blur="checkInputValue" placeholder="请填写内容" size="medium" v-model="form.name"
                    autocomplete="off"></el-input>
        </el-form-item>
        <el-form-item label="记录类型" :label-width="formLabelWidth">
          <el-input @blur="checkInputValue" size="medium" :disabled="true" v-if="is_op_type===2" v-model="form.type"
                    autocomplete="off"></el-input>
          <el-select size="medium" v-model="form.type" v-else placeholder="请选择记录类型" autocomplete="off"
                     style="width: 100%">
            <el-option label="NS" value="TEXT"></el-option>
            <el-option label="A" value="A"></el-option>
            <el-option label="AAAA" value="AAAA"></el-option>
            <el-option label="CNAME" value="CNAME"></el-option>
            <el-option label="MX" value="MX"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="MX" :label-width="formLabelWidth">
          <el-input placeholder="请填写内容" @blur="checkInputValue" size="medium" v-model="form.mx"
                    autocomplete="off"></el-input>
        </el-form-item>
        <el-form-item label="TTL" :label-width="formLabelWidth">
          <el-input placeholder="请填写内容" @blur="checkInputValue" size="medium" v-model="form.ttl"
                    autocomplete="off"></el-input>
        </el-form-item>
        <el-form-item label="地址" :label-width="formLabelWidth">
          <el-input placeholder="请填写内容" @blur="checkInputValue" size="medium" v-model="form.address"
                    autocomplete="off"></el-input>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button size="medium" @click="dialogFormVisible = false">取 消</el-button>
        <el-button size="medium" type="primary" @click="submit">确 定</el-button>
      </div>
    </el-dialog>
    <BaseTemplate router-name="域名列表" router-path="/" current-router-name="解析列表">
      <template v-slot:main>
        <div class="analysisContent">
          <div class="indexTable">
            <div class="search">
              <div class="input">
                <div>
                  <el-button size="medium" type="primary" @click="addAnalysisEvent"><i class="el-icon-plus"></i>&nbsp;添加解析
                  </el-button>
                </div>
                <div>
                  <el-input size="medium" suffix-icon="el-icon-search" v-model="search" placeholder="请输入解析名称"
                            @input="searchAnalysis"></el-input>
                </div>
              </div>
            </div>
            <div class="table">
              <el-table
                  :data="tableData"
                  style="width: 100%">
                <el-table-column
                    label="名称">
                  <template slot-scope="scope">
                    <span style="margin-left: 10px">{{ scope.row.name }}</span>
                  </template>
                </el-table-column>
                <el-table-column
                    label="记录类型">
                  <template slot-scope="scope">
                    <span style="margin-left: 10px">{{ scope.row.type }}</span>
                  </template>
                </el-table-column>
                <el-table-column
                    label="MX">
                  <template slot-scope="scope">
                    <span style="margin-left: 10px">{{ scope.row.mx }}</span>
                  </template>
                </el-table-column>
                <el-table-column
                    label="TTL">
                  <template slot-scope="scope">
                    <span style="margin-left: 10px">{{ scope.row.ttl }}</span>
                  </template>
                </el-table-column>
                <el-table-column
                    label="地址">
                  <template slot-scope="scope">
                    <span style="margin-left: 10px">{{ scope.row.address }}</span>
                  </template>
                </el-table-column>
                <el-table-column
                    label="状态">
                  <template slot-scope="scope">
                    <el-switch
                        v-model="scope.row.is_active" inactive-color="#ff4949" @change="analysisStatus($event, scope.row)">
                    </el-switch>
                  </template>
                </el-table-column>
                <el-table-column
                    label="创建时间">
                  <template slot-scope="scope">
                    <span style="margin-left: 10px">{{ scope.row.create_time }}</span>
                  </template>
                </el-table-column>
                <el-table-column label="操作">
                  <template slot-scope="scope">
                    <el-button
                        size="mini"
                        @click="editAnalysis(scope.$index, scope.row)">编辑
                    </el-button>
                    <el-button
                        size="mini"
                        type="danger"
                        @click="handleDelete(scope.row)">删除
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
            </div>
            <div class="block">
              <el-pagination
                  layout="prev, pager, next"
                  :total="analysisTotal" :current-page="page" @current-change="loadData">
              </el-pagination>
            </div>
          </div>
        </div>
      </template>
    </BaseTemplate>
  </div>
</template>

<script>
import BaseTemplate from "@/components/BaseTemplate";

export default {
  name: "analysis",
  components: {BaseTemplate},
  data() {
    return {
      page: 1,
      analysisTotal: 0,
      dialogVisible: false,
      domain: this.$route.query.domain,
      dialogFormVisible: false,
      dialogTitle: '',
      formLabelWidth: '70px',
      is_op_type: 0,
      form: {
        name: '',
        type: '',
        mx: 0,
        ttl: 600,
        address: '',
      },
      search: '',
      tableData: []
    }
  },
  methods: {
    analysisStatus(status, row){
      this.axios.post('/agent/resolve/stop/', {
        domain: this.domain,
        resolve_id: row.id,
        is_active: status,
      }, {
        headers: {
          'Authorization': this.$cookie.get('Token')
        }
      }).then(res =>{
        let msgType = 'success';
        if (res.data.code !== 200) {
          msgType = 'error';
        }
        this.$message({
          message: res.data.msg,
          type: msgType,
        });
        this.loadData(1);
      });
    },
    handleDelete(row) {
      this.axios.post('/agent/resolve/delete/', {
        domain: this.domain,
        resolve_id: row.id,
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
        this.loadData(1);
      })
    },
    checkInputValue(event) {
      if (event.target.value.trim().length === 0) {
        event.target.placeholder = "请填写内容";
      }
    },
    closeDialog() {
      this.form = {
        name: '',
        type: '',
        mx: 0,
        ttl: 600,
        address: '',
      }
    },
    submit() {
      for (let k in this.form) {
        if (this.form[k].toString().trim().length === 0) {
          this.$message({
            message: '表单没有填写完成!',
            type: 'error'
          })
          return;
        }
      }
      if (this.is_op_type === 1) {
        this.axios.post('/agent/resolve/create/', {
          domain: this.domain,
          name: this.form.name,
          mx: parseInt(this.form.mx),
          ttl: parseInt(this.form.ttl),
          address: this.form.address,
          type: this.form.type
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
        });
      } else if (this.is_op_type === 2) {
        this.axios.post('/agent/resolve/modify/', {
          resolve_id: this.form.id,
          domain: this.domain,
          mx: parseInt(this.form.mx),
          ttl: parseInt(this.form.ttl),
          address: this.form.address,
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

        });
      } else {
        this.$message({
          message: '没有做任何操作',
          type: 'info',
        })
      }
      this.dialogFormVisible = false;
      this.is_op_type = 0;
      this.dialogTitle = "";
      this.loadData(1);

    },
    searchAnalysis() {
      this.loadData(1);
    },
    editAnalysis(index, row) {
      this.form = {
        id: row.id,
        name: row.name.toString(),
        type: row.type.toString(),
        mx: row.mx.toString(),
        ttl: row.ttl.toString(),
        address: row.address.toString(),
      }
      this.dialogFormVisible = true;
      this.is_op_type = 2;
      this.dialogTitle = "修改记录";
    },
    addAnalysisEvent() {
      this.dialogFormVisible = true;
      this.is_op_type = 1;
      this.dialogTitle = "添加记录";
    },
    loadData(page) {
      this.page = page;
      this.axios.get('/agent/resolve/list/' + this.domain + '/?size=10&page=' + this.page + '&name=' + this.search, {
        headers: {
          'Authorization': this.$cookie.get('Token')
        }
      }).then(res => {
        this.tableData = res.data.data.data;
        this.analysisTotal = res.data.data.page_num.count;
      });
    }
  },
  mounted() {
    this.loadData(this.page);
  }
}
</script>

<style lang="scss" scoped>
.analysis {
  .analysisContent {
    display: flex;
    height: 100%;

    .indexTable {
      padding: 0 20px;
      width: 100%;
      margin-top: 10px;
      background-color: #FFFFFF;
      border: 1px solid #FFFFFF;
      border-radius: 5px;

      .search {
        margin: 20px 10px;

        .input {
          display: flex;

          div {
            margin-right: 20px;
          }
        }
      }

      .block {
        margin: 15px 0 100px;
      }
    }
  }
}

</style>