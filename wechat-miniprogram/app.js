App({
  globalData: {
    userInfo: null,
    token: null,
    apiBaseUrl: 'https://your-api-domain.com',
    ttsBaseUrl: 'https://your-tts-domain.com'
  },

  onLaunch() {
    // 检查登录态
    this.checkLoginStatus();
  },

  checkLoginStatus() {
    const token = wx.getStorageSync('token');
    if (token) {
      this.globalData.token = token;
    }
  },

  setToken(token) {
    this.globalData.token = token;
    wx.setStorageSync('token', token);
  },

  clearToken() {
    this.globalData.token = null;
    wx.removeStorageSync('token');
  }
});