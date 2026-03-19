Page({
  data: {
    userInfo: null,
    credits: 0,
    subscription: null,
    isLoggedIn: false
  },

  onLoad() {
    this.checkLoginStatus();
  },

  checkLoginStatus() {
    const token = getApp().globalData.token;
    this.setData({ isLoggedIn: !!token });
    if (token) {
      this.loadUserData();
    }
  },

  loadUserData() {
    this.setData({
      userInfo: { nickname: '准妈妈', phone: '138****8000' },
      credits: 100,
      subscription: { name: '月度套餐', expireDate: '2026-04-18' }
    });
  },

  onLogin() {
    wx.navigateTo({ url: '/pages/login/login' });
  },

  onLogout() {
    getApp().clearToken();
    this.setData({ isLoggedIn: false, userInfo: null });
  }
});