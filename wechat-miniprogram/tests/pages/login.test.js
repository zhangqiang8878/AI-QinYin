const path = require('path');

// Mock api module
jest.mock('../../utils/api', () => ({
  sendSmsCode: jest.fn(),
  login: jest.fn()
}));

describe('Login Page', () => {
  let pageOptions;

  beforeAll(() => {
    // Setup global WeChat miniprogram variables
    global.Page = (options) => {
      pageOptions = options;
    };
    
    // Load the script to register the page
    require('../../pages/login/login.js');
  });

  beforeEach(() => {
    // Set up global wx mock
    global.wx = {
      showToast: jest.fn(),
      navigateTo: jest.fn(),
      navigateBack: jest.fn()
    };
    
    // Set up global getApp mock
    global.getApp = jest.fn(() => ({
      setToken: jest.fn(),
      globalData: {
        userInfo: null
      }
    }));

    jest.clearAllMocks();
    
    // Reset data
    pageOptions.data = {
      phone: '',
      code: '',
      countdown: 0
    };
    
    // Mock setData
    pageOptions.setData = function(data) {
      Object.assign(this.data, data);
    };
  });

  describe('Phone input validation', () => {
    test('should show error for empty phone', async () => {
      await pageOptions.onSendCode();

      expect(global.wx.showToast).toHaveBeenCalledWith({
        title: '请输入正确的手机号',
        icon: 'none'
      });
    });

    test('should show error for invalid phone', async () => {
      pageOptions.setData({ phone: '1234567890' }); // 10 digits
      
      await pageOptions.onSendCode();

      expect(global.wx.showToast).toHaveBeenCalledWith({
        title: '请输入正确的手机号',
        icon: 'none'
      });
    });
  });

  describe('Send code function', () => {
    test('should call api and start countdown on success', async () => {
      pageOptions.setData({ phone: '13800138000' });

      const api = require('../../utils/api');
      api.sendSmsCode.mockResolvedValue({ success: true });

      await pageOptions.onSendCode();

      expect(api.sendSmsCode).toHaveBeenCalledWith('13800138000');
      expect(pageOptions.data.countdown).toBe(60);
      expect(global.wx.showToast).toHaveBeenCalledWith({
        title: '验证码已发送',
        icon: 'success'
      });
      
      // Cleanup timer created by test
      clearInterval(pageOptions.timer);
    });
  });
  
  describe('Login function', () => {
    test('should show error for empty code', async () => {
      pageOptions.setData({ phone: '13800138000', code: '' });
      
      await pageOptions.onLogin();

      expect(global.wx.showToast).toHaveBeenCalledWith({
        title: '请输入验证码',
        icon: 'none'
      });
    });

    test('should save token and navigate on successful login', async () => {
      pageOptions.setData({ phone: '13800138000', code: '123456' });

      const api = require('../../utils/api');
      api.login.mockResolvedValue({ 
        token: 'test-token',
        user: { id: 1, nickname: 'Test User' }
      });

      // Mock setTimeout to immediately execute
      jest.useFakeTimers();

      await pageOptions.onLogin();
      
      jest.runAllTimers();

      expect(api.login).toHaveBeenCalledWith('13800138000', '123456');
      expect(global.wx.showToast).toHaveBeenCalledWith({
        title: '登录成功',
        icon: 'success'
      });
      expect(global.wx.navigateBack).toHaveBeenCalled();
      
      jest.useRealTimers();
    });
  });
});