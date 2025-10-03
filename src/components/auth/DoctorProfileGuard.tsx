import React from 'react';
import { useAuth } from '@/contexts/AuthContext';
import DoctorProfileCompletion from '@/components/doctor/DoctorProfileCompletion';

interface DoctorProfileGuardProps {
  children: React.ReactNode;
}

const DoctorProfileGuard: React.FC<DoctorProfileGuardProps> = ({ children }) => {
  const { currentUser } = useAuth();

  // Si l'utilisateur n'est pas connecté, laisser passer (géré par ProtectedRoute)
  if (!currentUser) {
    return <>{children}</>;
  }

  // Si l'utilisateur est un médecin et n'a pas complété son profil
  if (currentUser.role === 'DOCTOR' && !currentUser.hasCompletedProfile) {
    return (
      <DoctorProfileCompletion
        onProfileCompleted={() => {
          // Recharger la page pour mettre à jour le contexte
          // Le AuthContext va maintenant vérifier le statut du profil
          window.location.reload();
        }}
      />
    );
  }

  // Sinon, afficher le contenu normal
  return <>{children}</>;
};

export default DoctorProfileGuard;
