Page({
  data: {
    historyList: [],
    loading: false,
    hasMore: true
  },

  onLoad() {
    this.loadHistory();
  },

  loadHistory() {
    // Mock data
    this.setData({
      historyList: [
        { id: 1, title: '睡前故事', createdAt: '2026-03-18', duration: '3:45' }
      ]
    });
  },

  onPlay(e) {
    const { id } = e.currentTarget.dataset;
    console.log('Play:', id);
  }
});