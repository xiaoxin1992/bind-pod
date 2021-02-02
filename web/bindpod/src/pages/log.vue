<template>
  <div class="log">
    <el-container>
      <el-row>
        <el-col>
          <div class="searchDiv">
            <el-form :inline="true" :model="search">
              <el-form-item label="操作用户">
                <el-input v-model="search.username" prefix-icon="el-icon-search" placeholder="用户名" size="medium" @input="timeRange"></el-input>
              </el-form-item>
              <el-form-item label="事件">
                <el-select v-model="search.eventType" placeholder="请选择" size="medium" @change="timeRange">
                  <el-option
                      v-for="item in eventOptions"
                      :key="item.value"
                      :label="item.label"
                      :value="item.value">
                  </el-option>
                </el-select>
              </el-form-item>
              <el-form-item label="操作时间">
                <el-date-picker size="medium"
                    v-model="search.time"
                    type="daterange"
                    start-placeholder="开始日期"
                    end-placeholder="结束日期"
                    :default-time="['00:00:00', '23:59:59']" value-format="yyyy-MM-dd" @change="timeRange">
                </el-date-picker>
              </el-form-item>
            </el-form>
          </div>
        </el-col>
        <el-col>
          <div class="data">
            <el-table ref="multipleTable" size="medium" v-loading="loading"  :data="tableData"
                      style="width: 100%">
              <el-table-column
                  label="操作人" prop="username" show-overflow-tooltip header-align="center" align="center">
              </el-table-column>
              <el-table-column
                  label="时间" show-overflow-tooltip header-align="center" align="center">
                <template slot-scope="scope">
                  <i class="el-icon-time"></i>
                  <span style="margin-left: 10px">{{ scope.row.create_time }}</span>
                </template>
              </el-table-column>
              <el-table-column
                  label="事件" prop="event" header-align="center" align="center">
              </el-table-column>
              <el-table-column label="内容" prop="content" header-align="center" align="center" width="600">
              </el-table-column>
            </el-table>
          </div>
          <div class="page block" v-show="!loading">
            <el-pagination
                background
                :current-page.sync="pagination.current"
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
export default {
  name: "log",
  data() {
    return {
      loading: false,
      pagination: {
        current: 1,
        total: 0,
        size: 10,
      },
      search: {
        username: '',
        eventType: '',
        time: []
      },
      tableData: [],
      eventOptions: [
        {value: '', label:'全部'},
        {value: 0, label:'登陆'},
        {value: 1, label:'域名'},
        {value: 2, label:'解析'},
        {value: 3, label:'用户'},
      ]

    }
  },
  methods: {
    setDefaultTime() {
      let nowDate = new Date();
      let timeStr = nowDate.getFullYear()+ '-' +  (nowDate.getMonth() + 1).toString().padStart(2, "0") + '-' + nowDate.getDate().toString().padStart(2, "0")
      let newDate = new Date(Date.parse(new Date())-604800000)
      let netStr = newDate.getFullYear()+ '-' +  (newDate.getMonth() + 1).toString().padStart(2, "0") + '-' + newDate.getDate().toString().padStart(2, "0")
      this.search.time = [netStr, timeStr];
    },
    timeRange() {
      this.pagination.current = 1
      this.getLogList()
    },
    pageDown(page){
      this.pagination.current = page
      this.getLogList();
    },
    getLogList(){
      let param = `username=${this.search.username}&event=${this.search.eventType}&start_time=${this.search.time[0]}&end_time=${this.search.time[1]}`
      let url = `/agent/log/?size=${this.pagination.size}&page=${this.pagination.current}&${param}`
      this.axios.get(url, {
        headers: {
          'Authorization': this.$cookie.get('token')
        }
      }).then(res => {
        this.tableData = res.data.data.data;
        this.pagination.total = res.data.data.page_num.count;
      });
    },
  },
  mounted() {
    this.setDefaultTime();
    this.getLogList();
  }
}
</script>

<style scoped lang="scss">
  .log {
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
