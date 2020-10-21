<template>
  <div class="addDomain">
    <BaseTemplate router-name="添加域名" router-path="/add">
      <template v-slot:main>
        <div class="addMain">
          <div class="addForm">
            <el-form ref="form" :model="form" label-width="100px">
              <el-form-item label="域名">
                <el-input v-model="form.name" size="medium"></el-input>
              </el-form-item>
              <el-form-item label="区域文件">
                <el-input v-model="form.path" size="medium"></el-input>
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="submit" size="medium">立即创建</el-button>
                <el-button @click="clear" size="medium">清除</el-button>
              </el-form-item>
            </el-form>
          </div>
        </div>
      </template>
    </BaseTemplate>
  </div>
</template>

<script>
import BaseTemplate from "@/components/BaseTemplate";

export default {
  name: "addDomain",
  data() {
    return {
      form: {
        name: '',
        path: '',
      }
    }
  },
  methods: {
    submit() {
      for (const key in this.form) {
          if (this.form[key].trim().length === 0){
            this.$message({
              message: '表单未填写完成',
              type: 'error'
            })
            return
          }
      }
      this.axios.post("/agent/domain/create/", {
        domain: this.form.name,
        path: this.form.path
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
    clear() {
      this.form =  {
        name: '',
        path: '',
        key: ''
      }
    }
  },
  components: {BaseTemplate}
}
</script>

<style lang="scss" scoped>
.addDomain {
  .addMain {
    background-color: #FFFFFF;
    height: 100%;
    border: 1px solid #FFFFFF;
    border-radius: 5px;

    .addForm {
      margin: 200px auto;
      width: 400px;
    }
  }
}
</style>