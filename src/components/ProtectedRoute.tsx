import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth, UserRole } from '@/contexts/AuthContext';

interface ProtectedRouteProps {
  children: React.ReactNode;
  allowedRoles?: UserRole[];
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  allowedRoles = ['ADMIN', 'DOCTOR', 'SECRETARY']
}) => {
  const { isAuthenticated, userData, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-medical"></div>
      </div>
    );
  }

  if (!isAuthenticated) {
    // Redirect to login if not authenticated
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Check if user has the required role
  if (userData && !allowedRoles.includes(userData.role)) {
    // Redirect to unauthorized page if user doesn't have the required role
    return <Navigate to="/unauthorized" state={{ from: location }} replace />;
  }

  return <>{children}</>;
};

export default ProtectedRoute;
