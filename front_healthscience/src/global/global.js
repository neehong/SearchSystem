// const baseUrl = 'http://ocserver.supersy.xyz';
// const baseUrl = `${location.origin}/backend`;
// const baseUrl = 'http://www.altersyu.cn';
const baseUrl = 'http://localhost:8000'

// const fileBaseUrl = 'http://132.232.28.188:3000';
// const fileBaseUrl = `${location.origin}/fileUp`
// const fileBaseUrl = 'http://localhost:3000';

const apiConfig = {
  // index
  index: {
    suggest: baseUrl + '/suggest/',
    search: baseUrl + '/search/',
    index: baseUrl + '/index/',
    top: baseUrl
  }
}
export default {
  apiConfig
}
