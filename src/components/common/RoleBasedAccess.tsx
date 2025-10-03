import React from 'react';
import { useAuth, UserRole } from '@/contexts/AuthContext';

interface RoleBasedAccessProps {
  allowedRoles?: UserRole[];
  requiredPermissions?: string[];
  children: React.ReactNode;
  fallback?: React.ReactNode;
  showFallback?: boolean;
}

/**
 * Composant pour contrôler l'accès basé sur les rôles et permissions
 * 
 * @param allowedRoles - Rôles autorisés à voir le contenu
 * @param requiredPermissions - Permissions spécifiques requises
 * @param children - Contenu à afficher si autorisé
 * @param fallback - Contenu alternatif si non autorisé
 * @param showFallback - Afficher le fallback ou rien du tout
 */
const RoleBasedAccess: React.FC<RoleBasedAccessProps> = ({
  allowedRoles = [],
  requiredPermissions = [],
  children,
  fallback = null,
  showFallback = false
}) => {
  const { userData, isAuthenticated } = useAuth();

  // Si pas authentifié, ne rien afficher
  if (!isAuthenticated || !userData) {
    return showFallback ? <>{fallback}</> : null;
  }

  // Vérification des rôles
  const hasRequiredRole = allowedRoles.length === 0 || allowedRoles.includes(userData.role);

  // Vérification des permissions spécifiques
  const hasRequiredPermissions = requiredPermissions.length === 0 || 
    requiredPermissions.every(permission => {
      // Vérifier si l'utilisateur a cette permission
      return userData.permissions && userData.permissions[permission as keyof typeof userData.permissions];
    });

  // Si autorisé, afficher le contenu
  if (hasRequiredRole && hasRequiredPermissions) {
    return <>{children}</>;
  }

  // Sinon, afficher le fallback ou rien
  return showFallback ? <>{fallback}</> : null;
};

export default RoleBasedAccess;
