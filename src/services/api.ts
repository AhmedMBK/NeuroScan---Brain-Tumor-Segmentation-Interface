/**
 * 🧠 CereBloom API Service
 * Service principal pour l'intégration avec le backend FastAPI
 */

const API_BASE = 'http://localhost:8000/api/v1';

// Types pour l'authentification
export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: UserResponse;
}

export interface UserResponse {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
  role: 'ADMIN' | 'DOCTOR' | 'SECRETARY';
  status: string;
  employee_id?: string;
  assigned_doctor_id?: string;  // ✅ AJOUTÉ : Pour les secrétaires assignées à un médecin
  created_at: string;
}

// Types pour les patients
export interface Patient {
  id: string;
  first_name: string;
  last_name: string;
  date_of_birth: string;
  gender: 'MALE' | 'FEMALE';
  email?: string;
  phone?: string;
  address?: string;
  blood_type?: string;
  height?: number;
  weight?: number;
  emergency_contact?: any;
  medical_history?: any;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

// Types pour la segmentation IA
export interface AISegmentation {
  id: string;
  patient_id: string;
  doctor_id?: string;
  status: 'PROCESSING' | 'COMPLETED' | 'FAILED' | 'VALIDATED';
  volume_analysis?: any;
  confidence_score?: number;
  processing_time?: string;
  started_at: string;
  completed_at?: string;
  validated_at?: string;
}

export interface TumorSegment {
  id: string;
  segment_type: 'NECROTIC_CORE' | 'PERITUMORAL_EDEMA' | 'ENHANCING_TUMOR';
  volume_cm3: number;
  percentage: number;
  color_code: string;
  confidence_score: number;
  description?: string;
}

export interface SegmentationResults {
  segmentation_id: string;
  status: string;
  processing_time: string;
  tumor_analysis: {
    total_volume_cm3: number;
    tumor_segments: Array<{
      type: string;
      name: string;
      volume_cm3: number;
      percentage: number;
      color_code: string;
      description: string;
    }>;
  };
  recommendations: string[];
}

export interface SliceInfo {
  index: number;
  name: string;
}

export interface ImageType {
  key: string;
  name: string;
}

export interface SlicesResponse {
  slices: SliceInfo[];
  image_types: ImageType[];
}

// Gestion des tokens
class TokenManager {
  private static readonly ACCESS_TOKEN_KEY = 'cerebloom_access_token';
  private static readonly REFRESH_TOKEN_KEY = 'cerebloom_refresh_token';

  static getAccessToken(): string | null {
    return localStorage.getItem(this.ACCESS_TOKEN_KEY);
  }

  static setTokens(accessToken: string, refreshToken: string): void {
    localStorage.setItem(this.ACCESS_TOKEN_KEY, accessToken);
    localStorage.setItem(this.REFRESH_TOKEN_KEY, refreshToken);
  }

  static clearTokens(): void {
    localStorage.removeItem(this.ACCESS_TOKEN_KEY);
    localStorage.removeItem(this.REFRESH_TOKEN_KEY);
  }

  static getAuthHeaders(): HeadersInit {
    const token = this.getAccessToken();
    return token ? { 'Authorization': `Bearer ${token}` } : {};
  }
}

// Classe principale du service API
class CereBloomAPI {
  private baseURL: string;

  constructor(baseURL: string = API_BASE) {
    this.baseURL = baseURL;
  }

  // Méthode publique pour obtenir les headers d'authentification
  getAuthHeaders() {
    return TokenManager.getAuthHeaders();
  }

  // Méthode GET simplifiée
  async get<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'GET' });
  }

  // Méthode POST simplifiée
  async post<T>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  // Méthode générique pour les requêtes
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;

    // Ne pas définir Content-Type pour FormData (le navigateur le fait automatiquement)
    const headers: HeadersInit = {
      ...TokenManager.getAuthHeaders(),
      ...(options.headers as Record<string, string>),
    };

    // Ajouter Content-Type seulement si ce n'est pas FormData
    if (!(options.body instanceof FormData)) {
      (headers as Record<string, string>)['Content-Type'] = 'application/json';
    }

    const config: RequestInit = {
      headers,
      ...options,
    };

    try {
      const response = await fetch(url, config);

      if (!response.ok) {
        if (response.status === 401) {
          TokenManager.clearTokens();
          window.location.href = '/login';
          throw new Error('Session expirée');
        }

        const errorData = await response.json().catch(() => ({}));
        console.error('Détails de l\'erreur API:', errorData);

        // Améliorer l'affichage des erreurs de validation
        if (response.status === 422 && errorData.detail && Array.isArray(errorData.detail)) {
          const validationErrors = errorData.detail.map((err: any) =>
            `${err.loc?.join('.')} : ${err.msg}`
          ).join(', ');
          throw new Error(`Erreurs de validation: ${validationErrors}`);
        }

        throw new Error(errorData.detail || JSON.stringify(errorData) || `Erreur HTTP: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`Erreur API ${endpoint}:`, error);
      throw error;
    }
  }

  // === AUTHENTIFICATION ===

  async login(credentials: LoginRequest): Promise<LoginResponse> {
    const response = await this.request<LoginResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({
        email: credentials.email,
        password: credentials.password
      }),
    });

    TokenManager.setTokens(response.access_token, response.refresh_token);
    return response;
  }

  async logout(): Promise<void> {
    TokenManager.clearTokens();
  }

  async getCurrentUser(): Promise<UserResponse> {
    return this.request<UserResponse>('/auth/me');
  }



  // === PATIENTS ===

  async getPatients(page: number = 1, size: number = 10): Promise<PaginatedResponse<Patient>> {
    return this.request<PaginatedResponse<Patient>>(`/patients?page=${page}&size=${size}`);
  }

  async createPatient(patient: Partial<Patient>): Promise<Patient> {
    return this.request<Patient>('/patients', {
      method: 'POST',
      body: JSON.stringify(patient),
    });
  }

  async getPatient(id: string): Promise<Patient> {
    return this.request<Patient>(`/patients/${id}`);
  }

  async updatePatient(id: string, patient: Partial<Patient>): Promise<Patient> {
    return this.request<Patient>(`/patients/${id}`, {
      method: 'PUT',
      body: JSON.stringify(patient),
    });
  }

  // === SEGMENTATION IA ===

  async processPatientSegmentation(patientId: string): Promise<any> {
    return this.request<any>(`/segmentation/process-patient/${patientId}`, {
      method: 'POST',
    });
  }

  async getSegmentationStatus(segmentationId: string): Promise<AISegmentation> {
    return this.request<AISegmentation>(`/segmentation/status/${segmentationId}`);
  }

  async getSegmentationResults(segmentationId: string): Promise<SegmentationResults> {
    return this.request<SegmentationResults>(`/segmentation/results/${segmentationId}`);
  }

  async getTumorSegments(segmentationId: string): Promise<TumorSegment[]> {
    return this.request<TumorSegment[]>(`/segmentation/segments/${segmentationId}`);
  }

  async getPatientSegmentations(patientId: string, page: number = 1): Promise<PaginatedResponse<AISegmentation>> {
    return this.request<PaginatedResponse<AISegmentation>>(`/segmentation/patient/${patientId}?page=${page}`);
  }

  async validateSegmentation(segmentationId: string): Promise<any> {
    return this.request<any>(`/segmentation/validate/${segmentationId}`, {
      method: 'POST',
    });
  }

  async getSegmentationStatistics(): Promise<any> {
    return this.request<any>('/segmentation/statistics');
  }



  async clearPatientSegmentationHistory(patientId: string): Promise<any> {
    return this.request<any>(`/segmentation/patient/${patientId}/clear-history`, {
      method: 'DELETE',
    });
  }

  // === IMAGES MÉDICALES ===

  async uploadMedicalImages(patientId: string, uploadData: any): Promise<any> {
    // Créer FormData selon le format attendu par le backend
    const formData = new FormData();

    // Ajouter patient_id comme paramètre de formulaire
    formData.append('patient_id', patientId);

    // Ajouter les métadonnées optionnelles
    if (uploadData.acquisition_date) {
      formData.append('acquisition_date', uploadData.acquisition_date);
    }
    if (uploadData.notes) {
      formData.append('notes', uploadData.notes);
    }

    // Ajouter les fichiers selon les noms attendus par le backend
    uploadData.files.forEach((fileItem: any) => {
      const modalityName = fileItem.modality.toLowerCase();
      const fieldName = `${modalityName}_file`;
      formData.append(fieldName, fileItem.file);
    });

    return this.request<any>('/images/upload-modalities', {
      method: 'POST',
      body: formData,
      // Ne pas définir Content-Type pour FormData (le navigateur le fait automatiquement)
    });
  }

  async getPatientImages(patientId: string): Promise<any> {
    return this.request<any>(`/images/patient/${patientId}/modalities`);
  }

  async deleteImage(imageId: string): Promise<void> {
    return this.request<void>(`/images/${imageId}`, {
      method: 'DELETE',
    });
  }

  async deleteImageSeries(seriesId: string): Promise<void> {
    return this.request<void>(`/images/series/${seriesId}`, {
      method: 'DELETE',
    });
  }

  // === UTILISATEURS (ADMIN) ===

  async getUsers(page: number = 1, size: number = 10): Promise<PaginatedResponse<UserResponse>> {
    return this.request<PaginatedResponse<UserResponse>>(`/users?page=${page}&size=${size}`);
  }

  async createUser(userData: any): Promise<UserResponse> {
    return this.request<UserResponse>('/users', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  }

  async updateUser(id: string, userData: any): Promise<UserResponse> {
    return this.request<UserResponse>(`/users/${id}`, {
      method: 'PUT',
      body: JSON.stringify(userData),
    });
  }

  async deleteUser(id: string): Promise<void> {
    return this.request<void>(`/users/${id}`, {
      method: 'DELETE',
    });
  }

  // === MÉDECINS ===

  async getDoctors(): Promise<{ doctors: any[] }> {
    return this.request<{ doctors: any[] }>('/doctors');
  }

  async getDoctor(id: string): Promise<any> {
    return this.request<any>(`/doctors/${id}`);
  }

  async getDoctorsStats(): Promise<{
    total_doctors: number;
    completed_profiles: number;
    active_doctors: number;
    pending_profiles: number;
  }> {
    return this.request<{
      total_doctors: number;
      completed_profiles: number;
      active_doctors: number;
      pending_profiles: number;
    }>('/doctors/statistics');
  }

  // === COMPLÉTION PROFIL MÉDECIN ===

  async checkDoctorProfileStatus(): Promise<{ has_profile: boolean; doctor_id?: string }> {
    return this.request<{ has_profile: boolean; doctor_id?: string }>('/doctors/profile/status');
  }

  async completeDoctorProfile(profileData: any): Promise<any> {
    return this.request<any>('/doctors/complete-profile', {
      method: 'POST',
      body: JSON.stringify(profileData),
    });
  }

  // ✅ AJOUTÉ : Gestion des secrétaires par les médecins
  async createSecretary(secretaryData: any): Promise<any> {
    return this.request<any>('/doctors/create-secretary', {
      method: 'POST',
      body: JSON.stringify(secretaryData),
    });
  }

  async getMySecretaries(): Promise<any> {
    return this.request<any>('/doctors/my-secretaries');
  }

  // === TRAITEMENTS ===

  async getTreatments(patientId?: string): Promise<any[]> {
    const endpoint = patientId ? `/treatments?patient_id=${patientId}` : '/treatments';
    const response = await this.request<{treatments: any[]}>(endpoint);
    return response.treatments || [];
  }

  async createTreatment(treatmentData: any): Promise<any> {
    return this.request<any>('/treatments', {
      method: 'POST',
      body: JSON.stringify(treatmentData),
    });
  }

  async updateTreatment(id: string, treatmentData: any): Promise<any> {
    return this.request<any>(`/treatments/${id}`, {
      method: 'PUT',
      body: JSON.stringify(treatmentData),
    });
  }

  // === RENDEZ-VOUS ===

  async getAppointments(patientId?: string): Promise<any[]> {
    const url = patientId ? `/appointments?patient_id=${patientId}` : '/appointments';
    const response = await this.request<{appointments: any[]}>(url);
    return response.appointments || [];
  }

  async getAppointment(appointmentId: string): Promise<any> {
    return this.request<any>(`/appointments/${appointmentId}`);
  }

  async createAppointment(appointmentData: any): Promise<any> {
    return this.request<any>('/appointments', {
      method: 'POST',
      body: JSON.stringify(appointmentData),
    });
  }

  async updateAppointment(id: string, appointmentData: any): Promise<any> {
    return this.request<any>(`/appointments/${id}`, {
      method: 'PUT',
      body: JSON.stringify(appointmentData),
    });
  }

  async deleteAppointment(id: string): Promise<any> {
    return this.request<any>(`/appointments/${id}`, {
      method: 'DELETE',
    });
  }

  // === SEGMENTATIONS ===

  async getSegmentations(patientId?: string): Promise<any[]> {
    const url = patientId ? `/segmentation/patient/${patientId}` : '/segmentation';
    const response = await this.request<any>(url);
    return response.items || response.segmentations || [];
  }

  async getSegmentation(segmentationId: string): Promise<any> {
    return this.request<any>(`/segmentation/status/${segmentationId}`);
  }

  async createSegmentation(segmentationData: any): Promise<any> {
    return this.request<any>('/segmentation/create', {
      method: 'POST',
      body: JSON.stringify(segmentationData),
    });
  }

  async updateSegmentation(id: string, segmentationData: any): Promise<any> {
    return this.request<any>(`/segmentation/${id}`, {
      method: 'PUT',
      body: JSON.stringify(segmentationData),
    });
  }

  // === RAPPORTS DE SEGMENTATION ===

  async getReports(): Promise<any[]> {
    const response = await this.request<{reports: any[]}>('/reports');
    return response.reports || [];
  }

  async getReport(reportId: string): Promise<any> {
    return this.request<any>(`/reports/${reportId}`);
  }

  async createReport(reportData: any): Promise<any> {
    return this.request<any>('/reports', {
      method: 'POST',
      body: JSON.stringify(reportData),
    });
  }

  async updateReport(reportId: string, reportData: any): Promise<any> {
    return this.request<any>(`/reports/${reportId}`, {
      method: 'PUT',
      body: JSON.stringify(reportData),
    });
  }

  async deleteReport(reportId: string): Promise<void> {
    return this.request<void>(`/reports/${reportId}`, {
      method: 'DELETE',
    });
  }

  async getPatientReports(patientId: string): Promise<any[]> {
    const response = await this.request<{reports: any[]}>(`/reports?patient_id=${patientId}`);
    return response.reports || [];
  }

  async getSegmentationReports(segmentationId: string): Promise<any[]> {
    const response = await this.request<{reports: any[]}>(`/reports?segmentation_id=${segmentationId}`);
    return response.reports || [];
  }

  async downloadReport(reportId: string): Promise<void> {
    const token = localStorage.getItem('token');
    if (!token) {
      throw new Error('Token d\'authentification manquant');
    }

    const response = await fetch(`${this.baseURL}/reports/${reportId}/download`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || 'Erreur lors du téléchargement');
    }

    // Récupérer le nom du fichier depuis les headers
    const contentDisposition = response.headers.get('Content-Disposition');
    let filename = `rapport_${reportId.slice(0, 8)}.txt`;

    if (contentDisposition) {
      const filenameMatch = contentDisposition.match(/filename="?([^"]+)"?/);
      if (filenameMatch) {
        filename = filenameMatch[1];
      }
    }

    // Créer un blob et déclencher le téléchargement
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  }

  // === STATISTIQUES ===

  async getDashboardStats(): Promise<any> {
    return this.request<any>('/patients/statistics');
  }

  async getPatientsStatistics(): Promise<any> {
    return this.request<any>('/patients/statistics');
  }
}

// Instance singleton
export const cerebloomAPI = new CereBloomAPI();

// Export des types et du service
export { TokenManager };
export default cerebloomAPI;
