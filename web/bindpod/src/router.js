import Vue from 'vue'
import Router from 'vue-router'

Vue.use(Router);

export default new Router({
    routes: [
        {
            path: '/',
            redirect: '/domain'
        },
        {
            path:'/login',
            name: 'login',
            component: () => import('./pages/login'),
        },
        {
            path:'/domain',
            component: () => import('./pages/index'),
            children: [
                {
                    path: '',
                    name: 'domain',
                    component: () => import('./pages/domain')
                },
                {
                    path: 'analysis',
                    name: 'analysis',
                    component: () => import('./pages/analysis')
                },
            ]
        },

        {
            path:'/add',
            name: 'add',
            component: () => import('./pages/addDomain'),
        },
        {
            path:'/user',
            name: 'user',
            component: () => import('./pages/userInfo'),
        },
        {
            path:'/logs',
            name: 'log',
            component: () => import('./pages/logs'),
        }
    ]
})