import request from '../utils/request'

export function getCaptcha(data: any) {
  return request.post('/captcha/get', data)
}

export function checkCaptcha(data: any) {
  return request.post('/captcha/check', data)
}
