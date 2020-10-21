<template>
  <div class="log">
    <BaseTemplate router-name="操作日志" router-path="/logs">
      <template v-slot:main>
        <div class="logMain">
          <div class="search">
            <div class="searchItem">
              <span>操作人</span>
              <el-input
                  placeholder="请输入用户名"
                  v-model="username" size="medium" @input="search">
              </el-input>
            </div>
            <div class="searchItem">
              <span>事件类型</span>
              <el-select v-model="eventType" placeholder="请选择" @change="eventChange">
                <el-option
                    v-for="item in eventOptions"
                    :key="item.value"
                    :label="item.label"
                    :value="item.value">
                </el-option>
              </el-select>
            </div>
            <div class="searchItem">
              <span>操作时间</span>
              <el-date-picker
                  v-model="value"
                  type="daterange"
                  start-placeholder="开始日期"
                  end-placeholder="结束日期"
                  :default-time="['00:00:00', '23:59:59']" @change="filterTime" value-format="yyyy-MM-dd">
              </el-date-picker>
            </div>
          </div>
          <div class="tableMain">
            <el-table
                :data="tableData"
                style="width: 100%">
              <el-table-column
                  prop="username"
                  label="操作人">
              </el-table-column>
              <el-table-column
                  prop="create_time"
                  label="时间">
              </el-table-column>
              <el-table-column
                  prop="event"
                  label="事件">
              </el-table-column>
              <el-table-column
                  prop="content"
                  label="操作内容" width="600">
              </el-table-column>
            </el-table>
            <div class="block">
              <el-pagination
                  layout="prev, pager, next"
                  :total="logTotal" :page-size="pageSize" :current-page="page" @current-change="loadData">
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
  name: "log",
  data(){
    return {
      value: [],
      page: 1,
      logTotal: 0,
      pageSize: 10,
      username: '',
      eventType: '',
      tableData: [],
      start_time: "",
      end_time: "",
      eventOptions: [
        {value: '', label:'全部'},
        {value: 0, label:'登陆'},
        {value: 1, label:'域名'},
        {value: 2, label:'解析'},
        {value: 3, label:'用户'},
      ]
    }
  },
  components: {BaseTemplate},
  methods: {
    filterTime(data){
      this.start_time = data[0];
      this.end_time = data[1];
      this.loadData(1)
    },
    eventChange(value){
      this.eventType = value;
      this.loadData(1);
    },
    search(search){
      this.username = search;
      this.loadData(1);
    },
    loadData(page) {
      this.page = page
      let uri = "&username=" +  this.username + "&event=" + this.eventType + "&start_time="+this.start_time+"&end_time="+ this.end_time;
      this.axios.get("/agent/log/?size=10&page=" + this.page + uri, {
        headers: {
          'Authorization': this.$cookie.get('Token')
        }
      }).then(res => {
        this.tableData = res.data.data.data;
        this.logTotal = res.data.data.page_num.count;
      });
    }
  },
  mounted() {
    this.loadData(this.page);
  }
}
</script>

<style lang="scss" scoped>
.logMain {
  border-radius: 5px;
  height: 100%;
  background-color: #FFFFFF;
  color: #333333;
  font-size: 14px;
  .tableMain {
    padding: 0 20px;
    height: 100%;
    margin-top: 10px;
    background-color: #FFFFFF;
    border: 1px solid #FFFFFF;
    border-radius: 5px;
    .block {
      margin: 15px 0 100px;
    }
  }

  .search {
    display: flex;
    .searchItem{
      margin-left: 20px;
      margin-top: 30px;
      span{
        margin-left: 10px;
        width: 100px;
        height: 36px;
        line-height: 36px;
      }
      display: flex;
      width: 350px;
    }
  }
}
</style>