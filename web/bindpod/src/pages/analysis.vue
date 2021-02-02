<template>
  <div class="analysis">
    <el-container>
      <el-row>
        <el-col class="aHeader">
          <el-form :inline="true">
            <el-form-item>
              <el-button size="medium" plain @click="addAnalysis">添加解析</el-button>
            </el-form-item>
            <el-form-item>
              <el-input size="medium" v-model='search' @input="searchAnalysis" prefix-icon="el-icon-search"
                        placeholder="请输入解析名称"></el-input>
            </el-form-item>
          </el-form>
        </el-col>
        <el-col>
          <div class="data">
            <el-table ref="multipleTable" :data="pagination.analysisList" size="medium" v-loading="loading"
                      width="100%">
              <el-table-column
                  label="名称" prop="name" show-overflow-tooltip header-align="center" align="center" width="120px">
              </el-table-column>
              <el-table-column label="记录类型" prop="type" show-overflow-tooltip header-align="center" align="center">
              </el-table-column>
              <el-table-column
                  label="MX" prop="mx" header-align="center" align="center" width="50px">
              </el-table-column>
              <el-table-column
                  label="TTL" prop="ttl" header-align="center" align="center">
              </el-table-column>
              <el-table-column
                  label="地址" prop="address" header-align="center" align="center">
              </el-table-column>
              <el-table-column label="状态" header-align="center" align="center">
                <template slot-scope="scope">
                  <el-switch
                      v-model="scope.row.is_active" active-color="#13ce66" inactive-color="#ff4949"
                      @change="analysisStatus($event, scope.row)">
                  </el-switch>
                </template>
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
                      size="mini" plain @click="analysisHandle(scope.row)">编辑
                  </el-button>
                  <el-button
                      size="mini" plain type="danger" @click="analysisDelete(scope.row)">删除
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
      <el-dialog :title="DialogTitle" :visible.sync="dialogAnalysis" :modal-append-to-body='false' width="580px"
                 @closed="clearDialog">
        <el-form :model="form" status-icon :rules="rules" ref="form" :inline="true" size="small" label-position="right"
                 label-width="68px">
          <el-form-item prop="name" label="解析名称">
            <el-input v-model="form.name" placeholder="解析名称" size="small" clearable
                      :disabled="form.nameDisable"></el-input>
          </el-form-item>
          <el-form-item prop="selectValue" label="域名类型">
            <el-select v-model="form.selectValue" placeholder="请选择域名类型">
              <el-option v-for="item in options" :key="item.value" :label="item.label" :value="item.value"
                         :disabled="form.typeDisable"></el-option>
            </el-select>
          </el-form-item>
          <el-form-item prop="address" label="解析地址">
            <el-input v-model="form.address" placeholder="解析地址" clearable size="small" style="width: 462px"></el-input>
          </el-form-item>
          <el-form-item prop="mx" label="MX值">
            <el-input v-model="form.mx" placeholder="MX" clearable size="small"></el-input>
          </el-form-item>
          <el-form-item prop="ttl" label="TTL值">
            <el-input v-model="form.ttl" placeholder="TTL" clearable size="small"></el-input>
          </el-form-item>
        </el-form>
        <span slot="footer" class="dialog-footer">
                  <el-button @click="dialogAnalysis = false" size="small">取 消</el-button>
                  <el-button type="primary" @click="Submit" size="small">确 定</el-button>
                </span>
      </el-dialog>
    </el-container>
  </div>
</template>

<script>
export default {
  name: "analysis",
  data() {
    let checkExists = (rule, value, callback) => {
      if (value === '') {
        switch (rule.field) {
          case 'name':
            callback(new Error('解析名称不能为空'));
            break;
          case 'selectValue':
            callback(new Error('解析类型不能为空'));
            break;
          case 'address':
            callback(new Error('解析地址不能为空'));
            break;
          case 'mx':
            callback(new Error('MX值不能为空'));
            break;
          case 'ttl':
            callback(new Error('TTL值不能为空'));
            break;
        }
      } else {
        if (rule.field === "mx" || rule.field === "ttl") {
          if (!Number.isInteger(value)) {
            callback(new Error('TTL值只能是数字'));
          }
        }
      }
      callback();
    }
    return {
      selectValue: '',
      options: [
        {
          value: 'CNAME',
          label: 'CNAME'
        },
        {
          value: 'MX',
          label: 'MX'
        },
        {
          value: 'A',
          label: 'A'
        },
        {
          value: 'TEXT',
          label: 'TEXT'
        },
        {
          value: 'AAAA',
          label: 'AAAA'
        }
      ],
      dialogAnalysis: false,
      form: {
        selectValue: '',
        id: 0,
        name: '',
        nameDisable: false,
        typeDisable: false,
        address: '',
        mx: 0,
        ttl: 600,
      },
      rules: {
        name: [{validator: checkExists, trigger: 'blur'}],
        selectValue: [{validator: checkExists, trigger: 'blur'}],
        address: [{validator: checkExists, trigger: 'blur'}],
        mx: [{validator: checkExists, trigger: 'blur'}],
        ttl: [{validator: checkExists, trigger: 'blur'}],
      },
      search: '',
      DialogTitle: '添加域名',
      loading: false,
      domain: this.$route.params.domain,
      pagination: {
        current: 1,
        size: 10,
        total: 10,
        analysisList: []
      }
    }
  },
  methods: {
    add() {
      this.axios.post('/agent/resolve/create/', {
        domain: this.domain,
        name: this.form.name,
        mx: parseInt(this.form.mx),
        ttl: parseInt(this.form.ttl),
        address: this.form.address,
        type: this.form.selectValue
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
        this.dialogAnalysis = false;
      }).catch(() => {
        this.tools.notify("添加解析失败", "提示", "error");
      });
    },
    edit() {
      this.axios.post('/agent/resolve/modify/', {
        resolve_id: this.form.id,
        domain: this.domain,
        mx: parseInt(this.form.mx),
        ttl: parseInt(this.form.ttl),
        address: this.form.address,
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
        this.dialogAnalysis = false;
      }).catch(() => {
        this.tools.notify("编辑解析失败", "提示", "error");
      });
    },
    Submit() {
      let {selectValue, name, address, mx, ttl} = this.form
      if (selectValue === '' || name === '' || address === '' || mx === '' || ttl === '') {
        this.$refs.form.validateField('selectValue');
        this.$refs.form.validateField('name');
        this.$refs.form.validateField('address');
        this.$refs.form.validateField('mx');
        this.$refs.form.validateField('ttl');
        return false;
      }
      if (this.DialogTitle === '添加域名') {
        this.add();
      } else {
        this.edit()
      }
    },
    addAnalysis() {
      this.DialogTitle = '添加域名';
      this.dialogAnalysis = true;
    },
    clearDialog() {
      this.DialogTitle = '添加域名';
      this.form = {
        selectValue: '',
        name: '',
        address: '',
        id: 0,
        nameDisable: false,
        typeDisable: false,
        mx: 0,
        ttl: 600,
      };
      this.$refs.form.resetFields('selectValue');
      this.$refs.form.resetFields('name');
      this.$refs.form.resetFields('address');
      this.$refs.form.resetFields('mx');
      this.$refs.form.resetFields('ttl');
    },
    analysisHandle(value) {
      this.form = {
        selectValue: value.type,
        name: value.name,
        address: value.address,
        nameDisable: true,
        typeDisable: true,
        id: value.id,
        mx: value.mx,
        ttl: value.ttl,
      };
      this.DialogTitle = '修改域名';
      this.dialogAnalysis = true;
    },
    searchAnalysis() {
      this.pagination.current = 1;
      this.loadData();
    },
    analysisDelete(row) {
      this.axios.post('/agent/resolve/delete/', {
        domain: this.domain,
        resolve_id: row.id,
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
        this.loadData();
      }).catch(() => {
        this.tools.notify("删除解析失败", "提示", "error");
      });
    },
    analysisStatus(status, row) {
      this.axios.post('/agent/resolve/stop/', {
        domain: this.domain,
        resolve_id: row.id,
        is_active: status,
      }, {
        headers: {
          'Authorization': this.$cookie.get('token')
        }
      }).then(res => {
        console.log(res)
        let msgType = 'success';
        if (res.data.code !== 200) {
          msgType = 'error';
        }
        this.tools.notify(res.data.msg, "提示", msgType);
      }).catch(() => {
        this.tools.notify("解析状态改变失败", "提示", "error");
      });
    },
    pageDown(page) {
      this.pagination.current = page;
      this.loadData();
    },
    loadData() {
      this.loading = true;
      let url = `/agent/resolve/list/${this.domain}/?size=${this.pagination.size}&page=${this.pagination.current}&name=${this.search}`;
      this.axios.get(url, {
        headers: {
          'Authorization': this.$cookie.get('token')
        }
      }).then(res => {
        this.pagination.analysisList = res.data.data.data;
        this.pagination.total = res.data.data.page_num.count;
      });
      this.loading = false;
    }

  },
  mounted() {
    this.loadData();
  },
}
</script>

<style scoped lang="scss">
.analysis {
  margin: 0 10px 10px 0;
  height: 100%;
  width: 100%;

  .aHeader {
    padding-top: 50px;
    padding-left: 50px;
  }

  .data {
    width: 90%;
    margin-left: 48px;

    .page {
      margin-top: 15px;
      text-align: center;
    }
  }

}
</style>
