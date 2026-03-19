const api = require('../../utils/api');

Page({
  data: {
    knowledgeList: [],
    recommendedContent: [],
    userInfo: null,
    loading: true
  },

  onLoad() {
    this.loadHomeData();
  },

  async loadHomeData() {
    try {
      // 这里先mock数据，后续接入真实API
      this.setData({
        knowledgeList: [
          { id: 1, title: '什么是胎教？', summary: '胎教是指通过外界刺激促进胎儿身心发育的过程...' },
          { id: 2, title: '最佳胎教时间', summary: '怀孕4个月开始是胎教的最佳时期...' }
        ],
        recommendedContent: [
          { id: 1, title: '睡前故事：小兔子的冒险', duration: '3:45', image: '' }
        ],
        loading: false
      });
    } catch (error) {
      wx.showToast({ title: error.message, icon: 'none' });
    }
  },

  onNavigateToGenerate() {
    wx.switchTab({ url: '/pages/generate/generate' });
  }
});