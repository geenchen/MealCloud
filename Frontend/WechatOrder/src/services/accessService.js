const ACCESS_GRANTED_KEY = 'wechat_access_granted'
const ACCESS_PASSWORD = import.meta.env.VITE_WECHAT_ACCESS_PASSWORD || ''

export const hasAccessGranted = () => sessionStorage.getItem(ACCESS_GRANTED_KEY) === '1'

export const verifyAccessPassword = (password) => {
  if (!ACCESS_PASSWORD) {
    return { ok: true, message: '' }
  }
  if (String(password || '') === ACCESS_PASSWORD) {
    return { ok: true, message: '' }
  }
  return { ok: false, message: '访问密码错误' }
}

export const markAccessGranted = () => {
  sessionStorage.setItem(ACCESS_GRANTED_KEY, '1')
}

export const clearAccessGranted = () => {
  sessionStorage.removeItem(ACCESS_GRANTED_KEY)
}
