import frontRequest from '../utils/frontRequest'

export function login(data: any) {
  return frontRequest.post('/auth/login/front', data)
}

export function getInfo() {
  return frontRequest.get('/auth/info/front')
}

export function logout() {
  return frontRequest.post('/auth/logout/front')
}

export function getCaptcha(data: any) {
  return frontRequest.post('/captcha/get', data)
}

export function checkCaptcha(data: any) {
  return frontRequest.post('/captcha/check', data)
}
