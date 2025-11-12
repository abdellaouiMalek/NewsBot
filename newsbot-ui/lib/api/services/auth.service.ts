import axiosInstance from '../axios-instance';
import {
  LoginRequest,
  LoginResponse,
  LoginResponseSchema,
  SignupRequest,
  UserSchema,
  type User,
} from '../schemas/auth.schema';

/**
 * Authentication API service
 */
export const authService = {
  /**
   * Login user
   */
  login: async (credentials: LoginRequest): Promise<LoginResponse> => {
    const response = await axiosInstance.post('/auth/login', credentials);
    return LoginResponseSchema.parse(response.data);
  },

  /**
   * Signup new user
   */
  signup: async (data: SignupRequest): Promise<LoginResponse> => {
    const response = await axiosInstance.post('/auth/signup', data);
    return LoginResponseSchema.parse(response.data);
  },

  /**
   * Logout user
   */
  logout: async (): Promise<void> => {
    await axiosInstance.post('/auth/logout');
    if (typeof window !== 'undefined') {
      localStorage.removeItem('auth_token');
    }
  },

  /**
   * Get current user
   */
  getCurrentUser: async (): Promise<User> => {
    const response = await axiosInstance.get('/auth/me');
    return UserSchema.parse(response.data);
  },

  /**
   * Refresh token
   */
  refreshToken: async (): Promise<{ token: string }> => {
    const response = await axiosInstance.post('/auth/refresh');
    return response.data;
  },
};
