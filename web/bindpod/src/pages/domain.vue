<template>
  <div class="index">
    <BaseTemplate router-name="域名列表" router-path="/">
      <template v-slot:main>
        <div class="indexMain">
          <div class="displayData">
            <div class="text"><i class="el-icon-s-home"></i></div>
            <div class="text"><span>{{ domain_total }}</span></div>
            <div class="text"><p>域名总数</p></div>
          </div>
          <div class="displayData">
            <div class="text"><i class="el-icon-s-order"></i></div>
            <div class="text"><span>{{ analysis_active_total }}</span></div>
            <div class="text"><p>解析数量</p></div>
          </div>
          <div class="displayData">
            <div class="text"><i class="el-icon-s-release"></i></div>
            <div class="text"><span>{{ analysis_stop_total }}</span></div>
            <div class="text"><p>暂停解析</p></div>
          </div>
        </div>
        <div class="domainTable">
          <div class="indexTable">
            <div class="search">
              <div class="input">
                <el-input size="medium" suffix-icon="el-icon-search" v-model="search" placeholder="请输入域名"
                          @input="searchDomain()"></el-input>
              </div>
            </div>
            <div class="table">
              <el-table
                  :data="tableData"
                  style="width: 100%">
                <el-table-column
                    label="域名">
                  <template slot-scope="scope">
                    <span style="margin-left: 10px">{{ scope.row.domain }}</span>
                  </template>
                </el-table-column>
                <el-table-column
                    label="区域文件位置">
                  <template slot-scope="scope">
                    <span style="margin-left: 10px">{{ scope.row.path }}</span>
                  </template>
                </el-table-column>
                <el-table-column
                    label="解析数量">
                  <template slot-scope="scope">
                    <span style="margin-left: 10px">{{ scope.row.analysis }}</span>
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
                        @click="jumpAnalysis(scope.$index, scope.row)">解析
                    </el-button>
                    <el-button
                        v-show="is_superuser"
                        size="mini"
                        type="danger"
                        @click="handleDelete(scope.$index, scope.row)">删除
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
            </div>
            <div class="block">
              <el-pagination
                  layout="prev, pager, next"
                  :total="domain_total" :current-page="page" :page-size="pageSize" @current-change="loadData">
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
  name: "index",
  components: {BaseTemplate},
  data() {
    return {
      page: 1,
      is_superuser: this.$cookie.get('is_superuser'),
      pageSize: 10,
      domain_total: 0,
      analysis_active_total: 0,
      analysis_stop_total: 0,
      tableData: [],
      search: ""
    }
  },
  methods: {
    jumpAnalysis(index, row) {
      this.$router.push({
        name: 'analysis',
        query: {
          domain: row.domain,
        }
      });
    },
    handleDelete(index, row) {
      this.$confirm('确定删除 "' + row.domain + '" 域名？', '删除', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
        center: true
      }).then(() => {
        this.axios.post("/agent/domain/delete/", {
          domain: row.domain
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
      })
    },
    searchDomain() {
      this.loadData(1)
    },
    loadData(page) {
      this.page = page
      this.axios.get("/agent/domain/?size=10&page=" + this.page + '&domain=' + this.search, {
        headers: {
          'Authorization': this.$cookie.get('Token')
        }
      }).then(res => {
        this.tableData = res.data.data.data;
        this.domain_total = res.data.data.page_num.count;
      });
      this.axios.get("/agent/domain/info/", {
        headers: {
          'Authorization': this.$cookie.get('Token')
        }
      }).then(res => {
        this.domain_total = res.data.data.domain_total
        this.analysis_active_total = res.data.data.analysis_active_total
        this.analysis_stop_total = res.data.data.analysis_stop_total
      });
    }
  },
  mounted() {
    this.loadData(this.page);
  },
}
</script>

<style lang="scss" scoped>
.index {
  .indexMain {
    display: flex;
    justify-content: space-between;

    .displayData {
      background-color: #FFFFFF;
      width: 230px;
      height: 80px;
      border: 1px solid #FFFFFF;
      border-radius: 5px;

      .text {
        &:first-child {
          margin-top: 10px;
        }

        color: #303133;
        font-size: 14px;
        font-weight: 3;
        margin-bottom: 10px;
      }
    }
  }

  .domainTable {
    height: 100%;

    .indexTable {
      padding: 0 20px;
      //width: 100%;
      height: 100%;
      margin-top: 10px;
      background-color: #FFFFFF;
      border: 1px solid #FFFFFF;
      border-radius: 5px;

      .search {
        margin: 30px 50px 0;

        .input {
          width: 200px;
        }
      }

      .block {
        margin: 15px 0 100px;
      }
    }

  }
}
</style>