const API_BASE_URL = 'http://localhost:5000/api';

class ApiService {
  constructor() {
    this.token = localStorage.getItem('token');
  }

  setToken(token) {
    this.token = token;
    localStorage.setItem('token', token);
  }

  removeToken() {
    this.token = null;
    localStorage.removeItem('token');
  }

  async request(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    if (this.token) {
      config.headers.Authorization = `Bearer ${this.token}`;
    }

    try {
      const response = await fetch(url, config);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Error en la solicitud');
      }

      return data;
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  }

  // Autenticación
  async register(userData) {
    const response = await this.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
    
    if (response.token) {
      this.setToken(response.token);
    }
    
    return response;
  }

  async login(credentials) {
    const response = await this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    });
    
    if (response.token) {
      this.setToken(response.token);
    }
    
    return response;
  }

  async verifyToken() {
    return await this.request('/auth/verify-token', {
      method: 'POST',
    });
  }

  logout() {
    this.removeToken();
  }

  // Planes de entrenamiento
  async generateWorkoutPlan(duration_weeks = 4) {
    return await this.request('/generate-workout-plan', {
      method: 'POST',
      body: JSON.stringify({ duration_weeks }),
    });
  }

  // Planes nutricionales
  async generateNutritionPlan(duration_weeks = 4) {
    return await this.request('/generate-nutrition-plan', {
      method: 'POST',
      body: JSON.stringify({ duration_weeks }),
    });
  }

  // Obtener mis planes
  async getMyPlans() {
    return await this.request('/my-plans');
  }

  // Feedback
  async submitFeedback(feedbackData) {
    return await this.request('/submit-feedback', {
      method: 'POST',
      body: JSON.stringify(feedbackData),
    });
  }

  // Progreso
  async addProgressEntry(progressData) {
    return await this.request('/progress', {
      method: 'POST',
      body: JSON.stringify(progressData),
    });
  }

  async getProgressEntries(days = 30) {
    return await this.request(`/progress?days=${days}`);
  }

  async getProgressStats() {
    return await this.request('/progress/stats');
  }

  async deleteProgressEntry(entryId) {
    return await this.request(`/progress/${entryId}`, {
      method: 'DELETE',
    });
  }

  // Health check
  async healthCheck() {
    return await this.request('/health');
  }
}

export default new ApiService();

