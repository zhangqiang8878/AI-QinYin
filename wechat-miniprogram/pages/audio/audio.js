const app = getApp();
const innerAudioContext = wx.createInnerAudioContext();

Page({
  data: {
    audioUrl: '',
    isPlaying: false,
    duration: '00:00',
    currentTime: '00:00',
    progress: 0,
    title: ''
  },

  onLoad(options) {
    const { id } = options;
    if (id) {
      this.loadAudioData(id);
    }
    this.setupAudio();
  },

  async loadAudioData(id) {
    try {
      const api = require('../../utils/api');
      const res = await api.getContentDetail(id);
      
      this.setData({
        title: res.title,
        audioUrl: res.oss_url
      });
      
      if (res.oss_url) {
        innerAudioContext.src = res.oss_url;
      }
    } catch (e) {
      wx.showToast({ title: e.message || '加载失败', icon: 'none' });
    }
  },

  setupAudio() {
    innerAudioContext.onPlay(() => {
      this.setData({ isPlaying: true });
    });

    innerAudioContext.onPause(() => {
      this.setData({ isPlaying: false });
    });

    innerAudioContext.onStop(() => {
      this.setData({ isPlaying: false });
    });

    innerAudioContext.onEnded(() => {
      this.setData({
        isPlaying: false,
        progress: 0,
        currentTime: '00:00'
      });
    });

    innerAudioContext.onTimeUpdate(() => {
      const current = innerAudioContext.currentTime;
      const duration = innerAudioContext.duration;
      
      this.setData({
        currentTime: this.formatTime(current),
        duration: this.formatTime(duration),
        progress: (current / duration) * 100
      });
    });

    innerAudioContext.onError((res) => {
      console.error('Audio play error:', res.errMsg);
      this.setData({ isPlaying: false });
      wx.showToast({ title: '播放失败', icon: 'none' });
    });
  },

  formatTime(seconds) {
    if (!seconds) return '00:00';
    const min = Math.floor(seconds / 60);
    const sec = Math.floor(seconds % 60);
    return `${min.toString().padStart(2, '0')}:${sec.toString().padStart(2, '0')}`;
  },

  togglePlay() {
    if (!this.data.audioUrl) {
      wx.showToast({ title: '音频暂未准备好', icon: 'none' });
      return;
    }

    if (this.data.isPlaying) {
      innerAudioContext.pause();
    } else {
      innerAudioContext.play();
    }
  },

  onUnload() {
    innerAudioContext.stop();
    innerAudioContext.destroy();
  }
});