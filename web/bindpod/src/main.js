import Vue from 'vue'
import axios from 'axios'
import VueAxios from 'vue-axios'
import App from './App.vue'
import router from "@/router";
import ElementUI from 'element-ui';
import 'element-ui/lib/theme-chalk/index.css';
import VueCookie from 'vue-cookie'

Vue.config.productionTip = false
axios.defaults.baseURL = 'http://192.168.117.128:8000/';
axios.defaults.timeout = 8000;
axios.interceptors.response.use(function (response) {
    // let res = response.data;
    let path = location.hash;
    if(response.status === 401){
        if (path !== "#/login") {
            window.location.href = '/#/login';
        }
    }
    return response
}, (err) => {
    let res = err.response;
    let path = location.hash;
    if(res === undefined) {
        ElementUI.Message({
            "message": "请求错误，请联系管理员查看服务是否正常",
            type: 'error'
        });
    }
    if(res.status === 401 || parseInt(res.data.msg.code) === 401){
        if (path !== "#/login") {
            window.location.href = '/#/login';
        }
    }else if(res.status === 403){
        ElementUI.Message({
            "message": "您没有当前页面访问权限，禁止访问",
            type: 'error'
        });
    }else{
        ElementUI.Message({
            "message": "请求错误，请联系管理员查看服务是否正常",
            type: 'error'
        });
    }
    return Promise.reject(res);
});
Vue.use(VueAxios, axios);
Vue.use(ElementUI);
Vue.use(VueCookie);
new Vue({
    render: h => h(App),
    router,
}).$mount('#app')
