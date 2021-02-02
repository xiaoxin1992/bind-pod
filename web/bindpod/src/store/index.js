import Vue from 'vue'
import Vuex from 'vuex'
import mutations from './mutations'
import actions from './action'

Vue.use(Vuex);

const state = {
    username: '',
    display_name: '',
    is_superuser: false
}
export default new Vuex.Store({
   state,
   mutations,
   actions,
});
