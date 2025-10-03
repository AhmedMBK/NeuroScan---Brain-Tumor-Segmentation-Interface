import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Users,
  UserPlus,
  Stethoscope,
  BarChart3,
  FileText,
  Upload,
  Calendar,
  Settings,
  Shield,
  Activity
} from 'lucide-react';

interface QuickNavProps {
  currentPage?: string;
  patientId?: string;
}

const QuickNavigation: React.FC<QuickNavProps> = ({ currentPage, patientId }) => {
  const navigate = useNavigate();
  const { userData } = useAuth();

  // Actions rapides selon le rôle
  const getQuickActions = () => {
    const actions = [];

    // Actions communes à tous
    actions.push({
      title: 'Patients',
      description: 'Voir tous les patients',
      icon: <Users className="h-5 w-5" />,
      action: () => navigate('/patients'),
      roles: ['ADMIN', 'DOCTOR', 'SECRETARY'],
      active: currentPage === 'patients'
    });

    actions.push({
      title: 'Nouveau Patient',
      description: 'Ajouter un patient',
      icon: <UserPlus className="h-5 w-5" />,
      action: () => navigate('/patients/new'),
      roles: ['ADMIN', 'DOCTOR', 'SECRETARY'],
      active: currentPage === 'patients-new'
    });

    // Actions spécifiques au patient actuel
    if (patientId) {
      actions.push({
        title: 'Upload Images',
        description: 'Télécharger des images',
        icon: <Upload className="h-5 w-5" />,
        action: () => navigate(`/patients/${patientId}/upload`),
        roles: ['ADMIN', 'DOCTOR', 'SECRETARY'],
        active: currentPage === 'upload'
      });

      actions.push({
        title: 'Historique Examens',
        description: 'Voir les examens',
        icon: <FileText className="h-5 w-5" />,
        action: () => navigate(`/patients/${patientId}/exam-history`),
        roles: ['ADMIN', 'DOCTOR', 'SECRETARY'],
        active: currentPage === 'exam-history'
      });

      actions.push({
        title: 'Suivi Traitements',
        description: 'Gérer les traitements',
        icon: <Activity className="h-5 w-5" />,
        action: () => navigate(`/patients/${patientId}/treatment-tracking`),
        roles: ['ADMIN', 'DOCTOR'],
        active: currentPage === 'treatment-tracking'
      });
    }

    // Actions pour médecins et admins
    if (userData?.role === 'ADMIN' || userData?.role === 'DOCTOR') {
      actions.push({
        title: 'Médecins',
        description: 'Gérer les médecins',
        icon: <Stethoscope className="h-5 w-5" />,
        action: () => navigate('/doctors'),
        roles: ['ADMIN', 'DOCTOR'],
        active: currentPage === 'doctors'
      });

      actions.push({
        title: 'Rapports',
        description: 'Voir les rapports',
        icon: <BarChart3 className="h-5 w-5" />,
        action: () => navigate('/reports'),
        roles: ['ADMIN', 'DOCTOR'],
        active: currentPage === 'reports'
      });
    }

    // Actions admin uniquement
    if (userData?.role === 'ADMIN') {
      actions.push({
        title: 'Administration',
        description: 'Gérer les utilisateurs',
        icon: <Shield className="h-5 w-5" />,
        action: () => navigate('/users'),
        roles: ['ADMIN'],
        active: currentPage === 'users'
      });
    }

    // Paramètres pour tous
    actions.push({
      title: 'Paramètres',
      description: 'Configuration',
      icon: <Settings className="h-5 w-5" />,
      action: () => navigate('/settings'),
      roles: ['ADMIN', 'DOCTOR', 'SECRETARY'],
      active: currentPage === 'settings'
    });

    // Filtrer selon le rôle
    return actions.filter(action => 
      action.roles.includes(userData?.role || 'SECRETARY')
    );
  };

  const quickActions = getQuickActions();

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">Navigation Rapide</CardTitle>
        <CardDescription>
          Accès rapide aux fonctionnalités principales
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
          {quickActions.map((action, index) => (
            <Button
              key={index}
              variant={action.active ? "default" : "outline"}
              className="h-auto p-4 flex flex-col items-center gap-2"
              onClick={action.action}
            >
              {action.icon}
              <div className="text-center">
                <div className="font-medium text-sm">{action.title}</div>
                <div className="text-xs text-muted-foreground">
                  {action.description}
                </div>
              </div>
            </Button>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};

export default QuickNavigation;
