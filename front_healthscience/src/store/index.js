import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

const store = new Vuex.Store({
  state: {
    mySearch: []
  },
  mutations: {
    setMySearch (state, mySearch) {
      state.mySearch = mySearch
      localStorage.setItem('mySearch', JSON.stringify(mySearch))
    }
  }
})

export default store
