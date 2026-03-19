Page({
  data: {
    historyList: [],
    loading: false,
    hasMore: true,
    page: 1
  },

  onLoad() {
    this.loadHistory();
  },

  onShow() {
    // Refresh history when showing the page
    this.setData({ page: 1, historyList: [] });
    this.loadHistory();
  },

  async loadHistory() {
    if (this.data.loading || !this.data.hasMore) return;

    this.setData({ loading: true });
    
    try {
      const api = require('../../utils/api');
      const res = await api.getHistory({ page: this.data.page, limit: 20 });
      
      this.setData({
        historyList: [...this.data.historyList, ...res.items],
        hasMore: res.pagination.page < res.pagination.pages,
        page: this.data.page + 1,
        loading: false
      });
    } catch (e) {
      this.setData({ loading: false });
      wx.showToast({ title: e.message || '加载失败', icon: 'none' });
    }
  },

  onReachBottom() {
    this.loadHistory();
  },

  onPlay(e) {
    const { id } = e.currentTarget.dataset;
    wx.navigateTo({
      url: `/pages/audio/audio?id=${id}`
    });
  }
});