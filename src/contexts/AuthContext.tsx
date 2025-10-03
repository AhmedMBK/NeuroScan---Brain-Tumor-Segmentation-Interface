import React, { createContext, useContext, useState, useEffect } from 'react';
import cerebloomAPI, { UserResponse, LoginRequest, TokenManager } from '@/services/api';
import { UserPermissions, getRolePermissions } from '@/utils/permissions';

export type UserRole = 'ADMIN' | 'DOCTOR' | 'SECRETARY';

export interface UserData {
  id: string;
  email: string;
  displayName: string;
  role: UserRole;
  first_name: string;
  last_name: string;
  employee_id?: string;
  createdAt: string;
  permissions?: UserPermissions;
  hasCompletedProfile?: boolean;
  doctorId?: string;
  assigned_doctor_id?: string;
}

interface AuthContextType {
  currentUser: UserData | null;
  userData: UserData | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  register: (email: string, password: string, displayName: string, role: UserRole) => Promise<void>;
  loading: boolean;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [currentUser, setCurrentUser] = useState<UserData | null>(null);
  const [userData, setUserData] = useState<UserData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const initAuth = async () => {
      const token = TokenManager.getAccessToken();

      if (token) {
        try {
          const user = await cerebloomAPI.getCurrentUser();

          let hasCompletedProfile = true;
          let doctorId = undefined;

          // Vérifier le statut du profil pour les médecins (même lors du rechargement)
          if (user.role === 'DOCTOR') {
            try {
              const profileStatus = await cerebloomAPI.checkDoctorProfileStatus();
              hasCompletedProfile = profileStatus.has_profile;
              doctorId = profileStatus.doctor_id;
            } catch (error) {
              console.warn('Erreur lors de la vérification du profil médecin:', error);
              hasCompletedProfile = false;
            }
          }

          const userData: UserData = {
            id: user.id,
            email: user.email,
            displayName: `${user.first_name} ${user.last_name}`,
            role: user.role,
            first_name: user.first_name,
            last_name: user.last_name,
            employee_id: user.employee_id,
            createdAt: user.created_at,
            permissions: getRolePermissions(user.role) as UserPermissions,
            hasCompletedProfile,
            doctorId,
            assigned_doctor_id: user.assigned_doctor_id,
          };

          setCurrentUser(userData);
          setUserData(userData);
        } catch (error) {
          console.error('Erreur lors de la récupération de l\'utilisateur:', error);
          TokenManager.clearTokens();
        }
      }

      setLoading(false);
    };

    initAuth();
  }, []);

  const login = async (email: string, password: string) => {
    try {
      setLoading(true);
      const response = await cerebloomAPI.login({ email, password });

      let hasCompletedProfile = true;
      let doctorId = undefined;

      // Vérifier le statut du profil pour les médecins
      if (response.user.role === 'DOCTOR') {
        try {
          const profileStatus = await cerebloomAPI.checkDoctorProfileStatus();
          hasCompletedProfile = profileStatus.has_profile;
          doctorId = profileStatus.doctor_id;
        } catch (error) {
          console.warn('Erreur lors de la vérification du profil médecin:', error);
          hasCompletedProfile = false;
        }
      }

      const userData: UserData = {
        id: response.user.id,
        email: response.user.email,
        displayName: `${response.user.first_name} ${response.user.last_name}`,
        role: response.user.role,
        first_name: response.user.first_name,
        last_name: response.user.last_name,
        employee_id: response.user.employee_id,
        createdAt: response.user.created_at,
        permissions: getRolePermissions(response.user.role) as UserPermissions,
        hasCompletedProfile,
        doctorId,
        assigned_doctor_id: response.user.assigned_doctor_id,
      };

      setCurrentUser(userData);
      setUserData(userData);
    } catch (error) {
      console.error('Erreur de connexion:', error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    try {
      await cerebloomAPI.logout();
      setCurrentUser(null);
      setUserData(null);
    } catch (error) {
      console.error('Erreur de déconnexion:', error);
      throw error;
    }
  };

  const register = async (email: string, password: string, displayName: string, role: UserRole) => {
    try {
      // Pour l'instant, l'inscription n'est pas implémentée côté backend
      // Les utilisateurs sont créés par les administrateurs
      throw new Error('L\'inscription n\'est pas disponible. Contactez votre administrateur.');
    } catch (error) {
      console.error('Erreur d\'inscription:', error);
      throw error;
    }
  };

  const value = {
    currentUser,
    userData,
    login,
    logout,
    register,
    loading,
    isAuthenticated: !!currentUser
  };

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
};
