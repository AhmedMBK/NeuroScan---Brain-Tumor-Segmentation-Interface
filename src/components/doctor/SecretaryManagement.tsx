import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { format } from 'date-fns';
import { 
  UserPlus, 
  Users, 
  Search, 
  MoreHorizontal,
  Edit,
  Mail,
  Phone,
  Calendar,
  Badge as BadgeIcon,
  UserCheck
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { useAuth } from '@/contexts/AuthContext';
import CreateSecretaryForm from './CreateSecretaryForm';
import { useMySecretaries } from '@/hooks/api/useSecretaries';

const SecretaryManagement: React.FC = () => {
  const { t } = useTranslation();
  const { userData } = useAuth();
  const [searchTerm, setSearchTerm] = useState('');
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);

  // Hook pour récupérer les secrétaires
  const { data: secretariesData, isLoading, error, refetch } = useMySecretaries();

  // Filtrage des secrétaires
  const filteredSecretaries = secretariesData?.secretaries?.filter((secretary: any) => {
    const matchesSearch = 
      secretary.first_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      secretary.last_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      secretary.email.toLowerCase().includes(searchTerm.toLowerCase());
    
    return matchesSearch;
  }) || [];

  const handleSecretaryCreated = () => {
    setIsCreateDialogOpen(false);
    refetch();
  };

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Users className="h-5 w-5" />
            Mes Secrétaires
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-8">
            <div className="text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-medical mx-auto mb-4"></div>
              <p className="text-muted-foreground">Chargement des secrétaires...</p>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Users className="h-5 w-5" />
            Mes Secrétaires
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-8">
            <div className="text-center">
              <div className="h-8 w-8 text-destructive mx-auto mb-4">⚠️</div>
              <p className="text-destructive">Erreur lors du chargement des secrétaires</p>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <Users className="h-5 w-5" />
              Mes Secrétaires
            </CardTitle>
            <CardDescription>
              Gérer les secrétaires assignées à votre cabinet médical
            </CardDescription>
          </div>
          <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
            <DialogTrigger asChild>
              <Button>
                <UserPlus className="mr-2 h-4 w-4" />
                Nouvelle Secrétaire
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
              <DialogHeader>
                <DialogTitle>Créer une nouvelle secrétaire</DialogTitle>
                <DialogDescription>
                  Ajoutez une secrétaire qui sera automatiquement assignée à votre cabinet
                </DialogDescription>
              </DialogHeader>
              <div className="max-h-[calc(90vh-120px)] overflow-y-auto pr-2">
                <CreateSecretaryForm onSuccess={handleSecretaryCreated} />
              </div>
            </DialogContent>
          </Dialog>
        </div>
      </CardHeader>
      <CardContent>
        {/* Statistiques rapides */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
            <div className="text-2xl font-bold text-blue-600">
              {secretariesData?.secretaries_count || 0}
            </div>
            <div className="text-sm text-blue-600">Total Secrétaires</div>
          </div>
          <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg">
            <div className="text-2xl font-bold text-green-600">
              {filteredSecretaries.filter((s: any) => s.status === 'ACTIVE').length}
            </div>
            <div className="text-sm text-green-600">Actives</div>
          </div>
          <div className="bg-purple-50 dark:bg-purple-900/20 p-4 rounded-lg">
            <div className="text-2xl font-bold text-purple-600">
              {secretariesData?.doctor_name || 'Dr. ' + userData?.displayName}
            </div>
            <div className="text-sm text-purple-600">Médecin Responsable</div>
          </div>
        </div>

        {/* Recherche */}
        <div className="flex items-center gap-4 mb-6">
          <div className="relative flex-1 max-w-sm">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Rechercher une secrétaire..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
        </div>

        {/* Table des secrétaires */}
        <div className="border rounded-lg">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Secrétaire</TableHead>
                <TableHead>Contact</TableHead>
                <TableHead>ID Employé</TableHead>
                <TableHead>Statut</TableHead>
                <TableHead>Créée le</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredSecretaries.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} className="text-center py-8">
                    <div className="text-muted-foreground">
                      {searchTerm 
                        ? 'Aucune secrétaire trouvée avec ces critères'
                        : 'Aucune secrétaire assignée. Créez votre première secrétaire.'
                      }
                    </div>
                  </TableCell>
                </TableRow>
              ) : (
                filteredSecretaries.map((secretary: any) => (
                  <TableRow key={secretary.id}>
                    <TableCell>
                      <div className="flex items-center gap-3">
                        <div className="h-8 w-8 rounded-full bg-purple-100 dark:bg-purple-800 flex items-center justify-center">
                          <span className="text-sm font-medium text-purple-600">
                            {secretary.first_name[0]}{secretary.last_name[0]}
                          </span>
                        </div>
                        <div>
                          <div className="font-medium">
                            {secretary.first_name} {secretary.last_name}
                          </div>
                          <div className="text-sm text-muted-foreground flex items-center gap-1">
                            <Mail className="h-3 w-3" />
                            {secretary.email}
                          </div>
                        </div>
                      </div>
                    </TableCell>
                    <TableCell>
                      {secretary.phone ? (
                        <div className="text-sm flex items-center gap-1">
                          <Phone className="h-3 w-3" />
                          {secretary.phone}
                        </div>
                      ) : (
                        <span className="text-muted-foreground">Non renseigné</span>
                      )}
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-1">
                        <BadgeIcon className="h-3 w-3" />
                        <span className="font-mono text-sm">{secretary.employee_id}</span>
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge variant={secretary.status === 'ACTIVE' ? 'default' : 'secondary'}>
                        {secretary.status === 'ACTIVE' ? 'Active' : 'Inactive'}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-sm text-muted-foreground">
                      {format(new Date(secretary.created_at), 'dd/MM/yyyy')}
                    </TableCell>
                    <TableCell className="text-right">
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="sm">
                            <MoreHorizontal className="h-4 w-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuLabel>Actions</DropdownMenuLabel>
                          <DropdownMenuSeparator />
                          <DropdownMenuItem>
                            <Edit className="mr-2 h-4 w-4" />
                            Modifier
                          </DropdownMenuItem>
                          <DropdownMenuItem>
                            <Calendar className="mr-2 h-4 w-4" />
                            Voir planning
                          </DropdownMenuItem>
                          <DropdownMenuSeparator />
                          <DropdownMenuItem>
                            <UserCheck className="mr-2 h-4 w-4" />
                            Gérer permissions
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  );
};

export default SecretaryManagement;
