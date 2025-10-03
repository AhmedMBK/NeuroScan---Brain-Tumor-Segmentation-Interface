import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { RefreshCw, Users, Hash, TrendingUp } from 'lucide-react';
import { toast } from 'sonner';

interface EmployeeIdStats {
  prefix: string;
  count: number;
  last_id: string | null;
  next_available: string;
}

interface StatisticsData {
  DOCTOR: EmployeeIdStats;
  SECRETARY: EmployeeIdStats;
  ADMIN: EmployeeIdStats;
}

const EmployeeIdStatistics: React.FC = () => {
  const [statistics, setStatistics] = useState<StatisticsData | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const fetchStatistics = async () => {
    try {
      setIsLoading(true);
      const response = await fetch('/api/users/employee-id/statistics', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (!response.ok) {
        throw new Error('Erreur lors de la récupération des statistiques');
      }

      const data = await response.json();
      setStatistics(data.data);
    } catch (error) {
      console.error('Erreur:', error);
      toast.error('Impossible de charger les statistiques');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchStatistics();
  }, []);

  const getRoleDisplayName = (role: string) => {
    const names = {
      DOCTOR: 'Médecins',
      SECRETARY: 'Secrétaires',
      ADMIN: 'Administrateurs'
    };
    return names[role as keyof typeof names] || role;
  };

  const getRoleColor = (role: string) => {
    const colors = {
      DOCTOR: 'bg-blue-50 text-blue-700 border-blue-200',
      SECRETARY: 'bg-green-50 text-green-700 border-green-200',
      ADMIN: 'bg-purple-50 text-purple-700 border-purple-200'
    };
    return colors[role as keyof typeof colors] || 'bg-gray-50 text-gray-700 border-gray-200';
  };

  const getRoleIcon = (role: string) => {
    const icons = {
      DOCTOR: '👨‍⚕️',
      SECRETARY: '👩‍💼',
      ADMIN: '👨‍💻'
    };
    return icons[role as keyof typeof icons] || '👤';
  };

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Hash className="h-5 w-5" />
            Statistiques Employee ID
          </CardTitle>
          <CardDescription>
            Chargement des statistiques...
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-8">
            <RefreshCw className="h-6 w-6 animate-spin text-muted-foreground" />
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!statistics) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Hash className="h-5 w-5" />
            Statistiques Employee ID
          </CardTitle>
          <CardDescription>
            Erreur lors du chargement des statistiques
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Button onClick={fetchStatistics} variant="outline">
            <RefreshCw className="h-4 w-4 mr-2" />
            Réessayer
          </Button>
        </CardContent>
      </Card>
    );
  }

  const totalUsers = Object.values(statistics).reduce((sum, stat) => sum + stat.count, 0);

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <Hash className="h-5 w-5" />
              Statistiques Employee ID
            </CardTitle>
            <CardDescription>
              Aperçu de la génération automatique des identifiants employés
            </CardDescription>
          </div>
          <Button onClick={fetchStatistics} variant="outline" size="sm">
            <RefreshCw className="h-4 w-4 mr-2" />
            Actualiser
          </Button>
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Résumé global */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-gradient-to-r from-blue-50 to-indigo-50 p-4 rounded-lg border">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-100 rounded-lg">
                <Users className="h-5 w-5 text-blue-600" />
              </div>
              <div>
                <div className="text-2xl font-bold text-blue-600">{totalUsers}</div>
                <div className="text-sm text-blue-600">Total Utilisateurs</div>
              </div>
            </div>
          </div>

          <div className="bg-gradient-to-r from-green-50 to-emerald-50 p-4 rounded-lg border">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-green-100 rounded-lg">
                <TrendingUp className="h-5 w-5 text-green-600" />
              </div>
              <div>
                <div className="text-2xl font-bold text-green-600">
                  {Object.keys(statistics).length}
                </div>
                <div className="text-sm text-green-600">Types de Rôles</div>
              </div>
            </div>
          </div>

          <div className="bg-gradient-to-r from-purple-50 to-violet-50 p-4 rounded-lg border">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-purple-100 rounded-lg">
                <Hash className="h-5 w-5 text-purple-600" />
              </div>
              <div>
                <div className="text-2xl font-bold text-purple-600">Auto</div>
                <div className="text-sm text-purple-600">Génération</div>
              </div>
            </div>
          </div>
        </div>

        {/* Détails par rôle */}
        <div className="space-y-4">
          <h3 className="text-lg font-medium">Détails par rôle</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {Object.entries(statistics).map(([role, stats]) => (
              <div key={role} className={`p-4 rounded-lg border ${getRoleColor(role)}`}>
                <div className="space-y-3">
                  {/* En-tête */}
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="text-lg">{getRoleIcon(role)}</span>
                      <span className="font-medium">{getRoleDisplayName(role)}</span>
                    </div>
                    <Badge variant="outline" className="text-xs">
                      {stats.prefix}XXX
                    </Badge>
                  </div>

                  {/* Statistiques */}
                  <div className="space-y-2">
                    <div className="flex justify-between items-center">
                      <span className="text-sm">Nombre total:</span>
                      <span className="font-semibold">{stats.count}</span>
                    </div>
                    
                    <div className="flex justify-between items-center">
                      <span className="text-sm">Dernier ID:</span>
                      <Badge variant="secondary" className="text-xs">
                        {stats.last_id || 'Aucun'}
                      </Badge>
                    </div>
                    
                    <div className="flex justify-between items-center">
                      <span className="text-sm">Prochain ID:</span>
                      <Badge className="text-xs bg-green-100 text-green-800 hover:bg-green-100">
                        {stats.next_available}
                      </Badge>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Informations sur le système */}
        <div className="bg-gray-50 p-4 rounded-lg border">
          <h4 className="font-medium mb-2">🔧 Système de génération automatique</h4>
          <div className="text-sm text-muted-foreground space-y-1">
            <p>• Les employee_id sont générés automatiquement si non spécifiés</p>
            <p>• Format: 3 lettres (rôle) + 3 chiffres (numéro séquentiel)</p>
            <p>• Exemples: DOC001, SEC045, ADM003</p>
            <p>• Garantie d'unicité et de séquentialité</p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default EmployeeIdStatistics;
