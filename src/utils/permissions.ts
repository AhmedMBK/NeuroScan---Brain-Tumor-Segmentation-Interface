import { UserRole } from '@/contexts/AuthContext';

// Types pour les permissions
export interface UserPermissions {
  can_view_patients: boolean;
  can_create_patients: boolean;
  can_edit_patients: boolean;
  can_delete_patients: boolean;
  can_view_segmentations: boolean;
  can_create_segmentations: boolean;
  can_validate_segmentations: boolean;
  can_manage_appointments: boolean;
  can_manage_users: boolean;
  can_view_reports: boolean;
  can_export_data: boolean;
}

export interface User {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
  role: UserRole;
  permissions?: UserPermissions;
  assigned_doctor_id?: string;  // ✅ AJOUTÉ : Pour les secrétaires assignées à un médecin
}

/**
 * Vérifie si un utilisateur a une permission spécifique
 */
export const checkPermission = (
  user: User | null,
  permission: keyof UserPermissions
): boolean => {
  if (!user?.permissions) return false;
  return user.permissions[permission];
};

/**
 * Vérifie si un utilisateur a un des rôles autorisés
 */
export const checkRole = (
  user: User | null,
  allowedRoles: UserRole[]
): boolean => {
  if (!user) return false;
  return allowedRoles.includes(user.role);
};

/**
 * Retourne les permissions par défaut selon le rôle
 */
export const getRolePermissions = (role: UserRole): Partial<UserPermissions> => {
  const permissions = {
    ADMIN: {
      can_view_patients: true,
      can_create_patients: true,
      can_edit_patients: true,
      can_delete_patients: true,
      can_view_segmentations: true,
      can_create_segmentations: true,
      can_validate_segmentations: true,
      can_manage_appointments: true,
      can_manage_users: true,
      can_view_reports: true,
      can_export_data: true,
    },
    DOCTOR: {
      can_view_patients: true,
      can_create_patients: true,
      can_edit_patients: true,
      can_delete_patients: false,
      can_view_segmentations: true,
      can_create_segmentations: true,
      can_validate_segmentations: true,
      can_manage_appointments: true,
      can_manage_users: false,
      can_view_reports: true,
      can_export_data: true,
    },
    SECRETARY: {
      can_view_patients: true,
      can_create_patients: true,
      can_edit_patients: true,
      can_delete_patients: false,
      can_view_segmentations: true,
      can_create_segmentations: false,  // ✅ CORRIGÉ : Secrétaires ne peuvent pas créer de segmentations
      can_validate_segmentations: false,
      can_manage_appointments: true,
      can_manage_users: false,
      can_view_reports: true,
      can_export_data: false,
    },
  };
  
  return permissions[role] || {};
};

/**
 * Hook personnalisé pour vérifier les permissions
 */
export const usePermissions = (user: User | null) => {
  return {
    canViewPatients: checkPermission(user, 'can_view_patients'),
    canCreatePatients: checkPermission(user, 'can_create_patients'),
    canEditPatients: checkPermission(user, 'can_edit_patients'),
    canDeletePatients: checkPermission(user, 'can_delete_patients'),
    canViewSegmentations: checkPermission(user, 'can_view_segmentations'),
    canCreateSegmentations: checkPermission(user, 'can_create_segmentations'),
    canValidateSegmentations: checkPermission(user, 'can_validate_segmentations'),
    canManageAppointments: checkPermission(user, 'can_manage_appointments'),
    canManageUsers: checkPermission(user, 'can_manage_users'),
    canViewReports: checkPermission(user, 'can_view_reports'),
    canExportData: checkPermission(user, 'can_export_data'),
    
    // Helpers pour les rôles
    isAdmin: checkRole(user, ['ADMIN']),
    isDoctor: checkRole(user, ['DOCTOR']),
    isSecretary: checkRole(user, ['SECRETARY']),
    isMedicalStaff: checkRole(user, ['DOCTOR', 'SECRETARY']),
  };
};
