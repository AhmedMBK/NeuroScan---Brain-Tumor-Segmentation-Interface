import React from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { useNavigate } from 'react-router-dom';
import {
  Users,
  Stethoscope,
  BarChart3,
  Shield,
  Settings,
  FileText,
  CheckCircle,
  XCircle
} from 'lucide-react';

const RoleNavigationTest: React.FC = () => {
  const { userData } = useAuth();
  const navigate = useNavigate();

  // Définir les routes et leurs restrictions
  const routes = [
    {
      path: '/dashboard',
      name: 'Tableau de bord',
      icon: <FileText className="h-4 w-4" />,
      allowedRoles: ['ADMIN', 'DOCTOR', 'SECRETARY'],
      description: 'Page d\'accueil principale'
    },
    {
      path: '/patients',
      name: 'Patients',
      icon: <Users className="h-4 w-4" />,
      allowedRoles: ['ADMIN', 'DOCTOR', 'SECRETARY'],
      description: 'Gestion des patients'
    },
    {
      path: '/doctors',
      name: 'Médecins',
      icon: <Stethoscope className="h-4 w-4" />,
      allowedRoles: ['ADMIN', 'DOCTOR'],
      description: 'Gestion des médecins'
    },
    {
      path: '/reports',
      name: 'Rapports',
      icon: <BarChart3 className="h-4 w-4" />,
      allowedRoles: ['ADMIN', 'DOCTOR'],
      description: 'Rapports et analyses'
    },
    {
      path: '/users',
      name: 'Administration',
      icon: <Shield className="h-4 w-4" />,
      allowedRoles: ['ADMIN'],
      description: 'Gestion des utilisateurs'
    },
    {
      path: '/settings',
      name: 'Paramètres',
      icon: <Settings className="h-4 w-4" />,
      allowedRoles: ['ADMIN', 'DOCTOR', 'SECRETARY'],
      description: 'Configuration du système'
    }
  ];

  const currentRole = userData?.role || 'SECRETARY';

  // Vérifier si l'utilisateur a accès à une route
  const hasAccess = (allowedRoles: string[]) => {
    return allowedRoles.includes(currentRole);
  };

  // Tester la navigation
  const testNavigation = (path: string, hasAccess: boolean) => {
    if (hasAccess) {
      navigate(path);
    } else {
      alert(`Accès refusé ! Votre rôle (${currentRole}) n'a pas accès à cette page.`);
    }
  };

  return (
    <Card className="w-full max-w-4xl mx-auto">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Shield className="h-5 w-5" />
          Test Navigation par Rôles
        </CardTitle>
        <CardDescription>
          Vérification des accès selon le rôle utilisateur actuel
        </CardDescription>
      </CardHeader>
      <CardContent>
        {/* Informations utilisateur actuel */}
        <div className="mb-6 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
          <div className="flex items-center gap-2 mb-2">
            <Badge variant="default" className="bg-blue-600">
              Rôle actuel: {currentRole}
            </Badge>
            <Badge variant="outline">
              Utilisateur: {userData?.displayName || 'Non connecté'}
            </Badge>
          </div>
          <p className="text-sm text-blue-700 dark:text-blue-300">
            Les boutons verts sont accessibles, les rouges sont interdits pour votre rôle.
          </p>
        </div>

        {/* Test des routes */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {routes.map((route) => {
            const access = hasAccess(route.allowedRoles);
            
            return (
              <div
                key={route.path}
                className={`p-4 border rounded-lg ${
                  access 
                    ? 'border-green-200 bg-green-50 dark:bg-green-900/20' 
                    : 'border-red-200 bg-red-50 dark:bg-red-900/20'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    {route.icon}
                    <span className="font-medium">{route.name}</span>
                  </div>
                  {access ? (
                    <CheckCircle className="h-5 w-5 text-green-600" />
                  ) : (
                    <XCircle className="h-5 w-5 text-red-600" />
                  )}
                </div>
                
                <p className="text-sm text-muted-foreground mb-3">
                  {route.description}
                </p>
                
                <div className="flex items-center justify-between">
                  <div className="text-xs">
                    <span className="text-muted-foreground">Autorisé pour: </span>
                    {route.allowedRoles.map((role, index) => (
                      <Badge 
                        key={role} 
                        variant="outline" 
                        className={`ml-1 ${role === currentRole ? 'bg-blue-100' : ''}`}
                      >
                        {role}
                      </Badge>
                    ))}
                  </div>
                  
                  <Button
                    size="sm"
                    variant={access ? "default" : "destructive"}
                    onClick={() => testNavigation(route.path, access)}
                    className="ml-2"
                  >
                    {access ? 'Accéder' : 'Tester'}
                  </Button>
                </div>
              </div>
            );
          })}
        </div>

        {/* Résumé des accès */}
        <div className="mt-6 p-4 bg-slate-50 dark:bg-slate-800 rounded-lg">
          <h4 className="font-medium mb-2">Résumé des accès pour {currentRole}:</h4>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-green-600 font-medium">
                ✅ Accès autorisé ({routes.filter(r => hasAccess(r.allowedRoles)).length})
              </span>
              <ul className="mt-1 space-y-1">
                {routes
                  .filter(r => hasAccess(r.allowedRoles))
                  .map(r => (
                    <li key={r.path} className="text-green-700 dark:text-green-300">
                      • {r.name}
                    </li>
                  ))
                }
              </ul>
            </div>
            <div>
              <span className="text-red-600 font-medium">
                ❌ Accès refusé ({routes.filter(r => !hasAccess(r.allowedRoles)).length})
              </span>
              <ul className="mt-1 space-y-1">
                {routes
                  .filter(r => !hasAccess(r.allowedRoles))
                  .map(r => (
                    <li key={r.path} className="text-red-700 dark:text-red-300">
                      • {r.name}
                    </li>
                  ))
                }
              </ul>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default RoleNavigationTest;
