import Vue from 'vue'
import Router from 'vue-router'

Vue.use(Router);
const includePush = Router.prototype.push

Router.prototype.push = function push(location) {
    return includePush.call(this, location).catch(err => err)

}
const router = new Router({
    routes: [
        {
            path:'/login',
            name: 'login',
            component: () => import('./pages/login'),
        },
        {
            path: '/',
            name: 'index',
            component: () => import('./pages/index'),
            redirect: '/domain',
            children: [
                {
                    path: 'domain',
                    name: 'domain',
                    component: ()=> import('./pages/domain'),
                    meta: {
                        name: '域名管理',
                        parent: '',
                        parentPath: '/'
                    },
                    children: [
                        {
                            path: 'analysis/:domain',
                            name: 'analysis',
                            component: () => import('./pages/analysis'),
                            meta: {
                                name: '域名解析',
                                parent: '域名管理',
                                parentPath: '/'
                            }
                        },
                    ],
                },
                {
                    path: 'log',
                    name: 'log',
                    component: ()=> import('./pages/log'),
                    meta: {
                        name: '操作日志',
                        parent: '',
                        parentPath: '/domain'
                    }
                },
                {
                    path: 'user',
                    name: ' user',
                    component: ()=> import('./pages/user'),
                    meta: {
                        name: '用户管理',
                        parent: '',
                        parentPath: '/'
                    }
                }
            ]

        }
    ],
});
export default router

