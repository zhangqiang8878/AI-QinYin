Page({
  data: {
    phone: '',
    code: '',
    countdown: 0
  },

  onInputPhone(e) {
    this.setData({ phone: e.detail.value });
  },

  onInputCode(e) {
    this.setData({ code: e.detail.value });
  },

  async onSendCode() {
    if (this.data.countdown > 0) return;
    if (!/^1\d{10}$/.test(this.data.phone)) {
      wx.showToast({ title: '请输入正确的手机号', icon: 'none' });
      return;
    }

    try {
      const api = require('../../utils/api');
      await api.sendSmsCode(this.data.phone);
      wx.showToast({ title: '验证码已发送', icon: 'success' });
      
      this.setData({ countdown: 60 });
      this.timer = setInterval(() => {
        if (this.data.countdown <= 1) {
          clearInterval(this.timer);
          this.setData({ countdown: 0 });
        } else {
          this.setData({ countdown: this.data.countdown - 1 });
        }
      }, 1000);
    } catch (e) {
      wx.showToast({ title: e.message || '发送失败', icon: 'none' });
    }
  },

  async onLogin() {
    if (!/^1\d{10}$/.test(this.data.phone)) {
      wx.showToast({ title: '请输入正确的手机号', icon: 'none' });
      return;
    }
    if (!this.data.code) {
      wx.showToast({ title: '请输入验证码', icon: 'none' });
      return;
    }

    try {
      const api = require('../../utils/api');
      const res = await api.login(this.data.phone, this.data.code);
      
      const app = getApp();
      app.setToken(res.token);
      app.globalData.userInfo = res.user;

      wx.showToast({ title: '登录成功', icon: 'success' });
      setTimeout(() => {
        wx.navigateBack();
      }, 1500);
    } catch (e) {
      wx.showToast({ title: e.message || '登录失败', icon: 'none' });
    }
  },

  onUnload() {
    if (this.timer) clearInterval(this.timer);
  }
});