import Vue from 'vue';
import App from './App.vue';
import router from './router';
import ElementUI from 'element-ui';
import VueCookie from 'vue-cookie'
import axios from "axios";
import store from './store'
import tools from './assets/js/tools'
import 'element-ui/lib/theme-chalk/index.css';

Vue.config.productionTip = false;
Vue.prototype.axios = axios;
Vue.prototype.tools = tools;
axios.defaults.baseURL = 'http://192.168.117.128:8000/';
axios.defaults.timeout = 8000;


// 拦截器
axios.interceptors.response.use(function (response) {
    let path = location.hash;
    if (response.status === 401) {
        if (path !== "#/login") {
            window.location.href = '/#/login';
        }
    }
    return response;
}, error => {
    let res = error.response;
    let path = location.hash;
    if (res === undefined) {
        ElementUI.Notification.error({
            title: "请求错误",
            message: "请联系管理员查看服务是否正常"
        });
        return;
    }
    if (res.status === 401 || parseInt(res.data.msg.code) === 401) {
        if (path !== "#/login") {
            window.location.href = '/#/login';
        }
    } else if (res.status === 403) {
        ElementUI.Notification.warning({
            title: "禁止访问",
            message: "您没有当前页面访问权限"
        });
    } else {
        ElementUI.Notification.error({
            title: "请求错误",
            message: "请联系管理员查看服务是否正常"
        });
        return;
    }
    return Promise.reject(res);
});

Vue.use(ElementUI);
Vue.use(VueCookie);
new Vue({
    router,
    store,
    render: h => h(App),
}).$mount('#app')
