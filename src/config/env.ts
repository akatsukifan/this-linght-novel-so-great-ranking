// 环境配置文件
// 在生产环境部署时，只需修改此文件中的API_BASE_URL

// 基础API地址
// 使用相对路径，让Nginx代理处理
export const API_BASE_URL = '/api';
export const DEBUG = false;

// 环境配置对象
export const env = {
  // API基础地址
  API_BASE_URL: API_BASE_URL,
  
  // 登录API路径
  LOGIN_URL: '/auth/login/',
  
  // 注册API路径
  REGISTER_URL: '/auth/register/',
  
  // 登出API路径
  LOGOUT_URL: '/logout/',
  
  // 小说列表API路径
  NOVELS_URL: '/novels/',
  
  // 购物车相关API路径
  CART_URL: '/cart/',
  CART_ADD_ITEM_URL: '/cart/add_item/',
  CART_UPDATE_ITEM_URL: '/cart/update_item/',
  CART_REMOVE_ITEM_URL: '/cart/remove_item/',
  CART_CLEAR_URL: '/cart/clear/',
};

// 拼接完整的API URL
export const getApiUrl = (path: string): string => {
  return `${env.API_BASE_URL}${path}`;
};