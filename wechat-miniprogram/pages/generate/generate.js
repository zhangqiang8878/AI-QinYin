Page({
  data: {
    currentStep: 1, // 1: 选择音色, 2: 选择内容类型, 3: 确认生成
    voices: [],
    selectedVoice: null,
    contentType: 'story', // story, music, poetry
    isGenerating: false
  },

  onLoad() {
    this.loadVoices();
  },

  loadVoices() {
    // Mock data for now
    this.setData({
      voices: [
        { id: 'v1', name: '爸爸的声音', isDefault: true },
        { id: 'v2', name: '妈妈的声音', isDefault: false }
      ]
    });
  },

  onSelectVoice(e) {
    const { id } = e.currentTarget.dataset;
    this.setData({ selectedVoice: id });
  },

  onSelectType(e) {
    const { type } = e.currentTarget.dataset;
    this.setData({ contentType: type });
  },

  onNextStep() {
    const { currentStep } = this.data;
    if (currentStep < 3) {
      this.setData({ currentStep: currentStep + 1 });
    }
  },

  onPrevStep() {
    const { currentStep } = this.data;
    if (currentStep > 1) {
      this.setData({ currentStep: currentStep - 1 });
    }
  },

  onGenerate() {
    wx.showToast({ title: '生成中...', icon: 'loading' });
  }
});