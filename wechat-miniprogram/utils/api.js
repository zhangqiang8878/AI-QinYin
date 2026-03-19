const app = getApp();

const API_BASE = 'https://your-api-domain.com/api';

function request(options) {
  return new Promise((resolve, reject) => {
    wx.request({
      url: `${API_BASE}${options.url}`,
      method: options.method || 'GET',
      data: options.data || {},
      header: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${app.globalData.token || ''}`
      },
      success: (res) => {
        if (res.statusCode === 200 && res.data.success) {
          resolve(res.data.data);
        } else if (res.statusCode === 401) {
          app.clearToken();
          wx.reLaunch({ url: '/pages/index/index' });
          reject(new Error('登录已过期'));
        } else {
          reject(new Error(res.data.message || '请求失败'));
        }
      },
      fail: reject
    });
  });
}

module.exports = {
  // 认证相关
  sendSmsCode: (phone) => request({ url: '/auth/sms-code', method: 'POST', data: { phone } }),
  login: (phone, code) => request({ url: '/auth/login', method: 'POST', data: { phone, code } }),

  // 用户相关
  getUserInfo: () => request({ url: '/users/me' }),
  updateUserInfo: (data) => request({ url: '/users/me', method: 'PUT', data }),

  // 音色相关
  getVoices: () => request({ url: '/voices' }),
  uploadVoiceSample: (formData) => request({ url: '/voices', method: 'POST', data: formData }),
  deleteVoice: (id) => request({ url: `/voices/${id}`, method: 'DELETE' }),

  // 内容生成
  generateContent: (data) => request({ url: '/contents', method: 'POST', data }),
  getHistory: (params) => request({ url: '/contents', data: params }),
  getContentDetail: (id) => request({ url: `/contents/${id}` }),

  // 支付相关
  getCredits: () => request({ url: '/users/credits' }),
  getSubscriptions: () => request({ url: '/subscriptions' }),
  createOrder: (data) => request({ url: '/payments/orders', method: 'POST', data }),

  request
};