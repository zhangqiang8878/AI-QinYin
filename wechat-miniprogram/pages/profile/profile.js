Page({
  data: {
    userInfo: null,
    credits: 0,
    subscription: null,
    isLoggedIn: false
  },

  onShow() {
    this.checkLoginStatus();
  },

  checkLoginStatus() {
    const token = getApp().globalData.token;
    this.setData({ isLoggedIn: !!token });
    if (token) {
      this.loadUserData();
    }
  },

  async loadUserData() {
    try {
      const api = require('../../utils/api');
      const userInfo = await api.getUserInfo();
      const creditsRes = await api.getCredits();
      const subRes = await api.getMySubscription();

      this.setData({
        userInfo: userInfo,
        credits: creditsRes.credits,
        subscription: subRes
      });
    } catch (e) {
      console.error('Load profile failed:', e);
    }
  },

  onLogin() {
    wx.navigateTo({ url: '/pages/login/login' });
  },

  onLogout() {
    getApp().clearToken();
    this.setData({ isLoggedIn: false, userInfo: null });
  },

  onNavigateToVoices() {
    wx.navigateTo({ url: '/pages/voices/voices' });
  },

  onNavigateToOrders() {
    wx.navigateTo({ url: '/pages/orders/orders' });
  },

  onNavigateToAbout() {
    wx.navigateTo({ url: '/pages/about/about' });
  }
});