import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { format } from 'date-fns';
import { 
  Users, 
  Plus, 
  Search, 
  Filter,
  MoreHorizontal,
  Edit,
  Trash2,
  UserCheck,
  UserX,
  Key,
  Shield,
  Mail,
  Phone
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
import { useUsers, useDeleteUser } from '@/hooks/api/useUsers';
import { UserRole } from '@/contexts/AuthContext';
import RoleBasedAccess from '@/components/common/RoleBasedAccess';

interface UserManagementProps {
  onCreateUser: () => void;
  onEditUser: (userId: string) => void;
}

const UserManagement: React.FC<UserManagementProps> = ({ onCreateUser, onEditUser }) => {
  const { t } = useTranslation();
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedRole, setSelectedRole] = useState<UserRole | 'ALL'>('ALL');
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 10;

  // Hooks API
  const { data: usersData, isLoading, error } = useUsers(currentPage, pageSize);
  const deleteUserMutation = useDeleteUser();

  // Filtrage des utilisateurs
  const filteredUsers = usersData?.items?.filter((user: any) => {
    const matchesSearch = 
      user.first_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user.last_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user.email.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesRole = selectedRole === 'ALL' || user.role === selectedRole;
    
    return matchesSearch && matchesRole;
  }) || [];

  // Gestion de la suppression
  const handleDeleteUser = async (userId: string, userName: string) => {
    if (window.confirm(`Êtes-vous sûr de vouloir supprimer l'utilisateur ${userName} ?`)) {
      try {
        await deleteUserMutation.mutateAsync(userId);
      } catch (error) {
        console.error('Erreur lors de la suppression:', error);
      }
    }
  };

  // Obtenir la couleur du badge selon le rôle
  const getRoleBadgeVariant = (role: UserRole) => {
    switch (role) {
      case 'ADMIN':
        return 'destructive';
      case 'DOCTOR':
        return 'default';
      case 'SECRETARY':
        return 'secondary';
      default:
        return 'outline';
    }
  };

  // Obtenir le statut utilisateur
  const getUserStatus = (user: any) => {
    // Logique pour déterminer le statut (actif/inactif)
    return user.is_active !== false ? 'Actif' : 'Inactif';
  };

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Users className="h-5 w-5" />
            Gestion des Utilisateurs
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-8">
            <div className="text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-medical mx-auto mb-4"></div>
              <p className="text-muted-foreground">Chargement des utilisateurs...</p>
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
            Gestion des Utilisateurs
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-8">
            <div className="text-center">
              <div className="h-8 w-8 text-destructive mx-auto mb-4">⚠️</div>
              <p className="text-destructive">Erreur lors du chargement des utilisateurs</p>
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
              Gestion des Utilisateurs
            </CardTitle>
            <CardDescription>
              Gérer les comptes utilisateurs, permissions et accès au système
            </CardDescription>
          </div>
          <RoleBasedAccess allowedRoles={['ADMIN']}>
            <Button onClick={onCreateUser}>
              <Plus className="mr-2 h-4 w-4" />
              Nouvel Utilisateur
            </Button>
          </RoleBasedAccess>
        </div>
      </CardHeader>
      <CardContent>
        {/* Filtres et recherche */}
        <div className="flex items-center gap-4 mb-6">
          <div className="relative flex-1 max-w-sm">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Rechercher un utilisateur..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
          
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline">
                <Filter className="mr-2 h-4 w-4" />
                {selectedRole === 'ALL' ? 'Tous les rôles' : selectedRole}
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent>
              <DropdownMenuItem onClick={() => setSelectedRole('ALL')}>
                Tous les rôles
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={() => setSelectedRole('ADMIN')}>
                Administrateur
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => setSelectedRole('DOCTOR')}>
                Médecin
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => setSelectedRole('SECRETARY')}>
                Secrétaire
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>

        {/* Statistiques rapides */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
            <div className="text-2xl font-bold text-blue-600">{usersData?.total || 0}</div>
            <div className="text-sm text-blue-600">Total Utilisateurs</div>
          </div>
          <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg">
            <div className="text-2xl font-bold text-green-600">
              {filteredUsers.filter((u: any) => u.role === 'DOCTOR').length}
            </div>
            <div className="text-sm text-green-600">Médecins</div>
          </div>
          <div className="bg-purple-50 dark:bg-purple-900/20 p-4 rounded-lg">
            <div className="text-2xl font-bold text-purple-600">
              {filteredUsers.filter((u: any) => u.role === 'SECRETARY').length}
            </div>
            <div className="text-sm text-purple-600">Secrétaires</div>
          </div>
          <div className="bg-red-50 dark:bg-red-900/20 p-4 rounded-lg">
            <div className="text-2xl font-bold text-red-600">
              {filteredUsers.filter((u: any) => u.role === 'ADMIN').length}
            </div>
            <div className="text-sm text-red-600">Administrateurs</div>
          </div>
        </div>

        {/* Table des utilisateurs */}
        <div className="border rounded-lg">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Utilisateur</TableHead>
                <TableHead>Rôle</TableHead>
                <TableHead>Statut</TableHead>
                <TableHead>Dernière connexion</TableHead>
                <TableHead>Créé le</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredUsers.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} className="text-center py-8">
                    <div className="text-muted-foreground">
                      {searchTerm || selectedRole !== 'ALL' 
                        ? 'Aucun utilisateur trouvé avec ces critères'
                        : 'Aucun utilisateur dans le système'
                      }
                    </div>
                  </TableCell>
                </TableRow>
              ) : (
                filteredUsers.map((user: any) => (
                  <TableRow key={user.id}>
                    <TableCell>
                      <div className="flex items-center gap-3">
                        <div className="h-8 w-8 rounded-full bg-medical/10 flex items-center justify-center">
                          <span className="text-sm font-medium text-medical">
                            {user.first_name[0]}{user.last_name[0]}
                          </span>
                        </div>
                        <div>
                          <div className="font-medium">
                            {user.first_name} {user.last_name}
                          </div>
                          <div className="text-sm text-muted-foreground flex items-center gap-1">
                            <Mail className="h-3 w-3" />
                            {user.email}
                          </div>
                        </div>
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge variant={getRoleBadgeVariant(user.role)}>
                        {user.role}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Badge variant={getUserStatus(user) === 'Actif' ? 'default' : 'secondary'}>
                        {getUserStatus(user)}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-sm text-muted-foreground">
                      {user.last_login ? format(new Date(user.last_login), 'dd/MM/yyyy HH:mm') : 'Jamais'}
                    </TableCell>
                    <TableCell className="text-sm text-muted-foreground">
                      {format(new Date(user.created_at), 'dd/MM/yyyy')}
                    </TableCell>
                    <TableCell className="text-right">
                      <RoleBasedAccess allowedRoles={['ADMIN']}>
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button variant="ghost" size="sm">
                              <MoreHorizontal className="h-4 w-4" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            <DropdownMenuLabel>Actions</DropdownMenuLabel>
                            <DropdownMenuSeparator />
                            <DropdownMenuItem onClick={() => onEditUser(user.id)}>
                              <Edit className="mr-2 h-4 w-4" />
                              Modifier
                            </DropdownMenuItem>
                            <DropdownMenuItem>
                              <Key className="mr-2 h-4 w-4" />
                              Réinitialiser mot de passe
                            </DropdownMenuItem>
                            <DropdownMenuItem>
                              <Shield className="mr-2 h-4 w-4" />
                              Gérer permissions
                            </DropdownMenuItem>
                            <DropdownMenuSeparator />
                            <DropdownMenuItem>
                              {getUserStatus(user) === 'Actif' ? (
                                <>
                                  <UserX className="mr-2 h-4 w-4" />
                                  Désactiver
                                </>
                              ) : (
                                <>
                                  <UserCheck className="mr-2 h-4 w-4" />
                                  Activer
                                </>
                              )}
                            </DropdownMenuItem>
                            <DropdownMenuSeparator />
                            <DropdownMenuItem 
                              className="text-destructive"
                              onClick={() => handleDeleteUser(user.id, `${user.first_name} ${user.last_name}`)}
                              disabled={deleteUserMutation.isPending}
                            >
                              <Trash2 className="mr-2 h-4 w-4" />
                              Supprimer
                            </DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </RoleBasedAccess>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </div>

        {/* Pagination */}
        {usersData && usersData.pages > 1 && (
          <div className="flex items-center justify-between mt-6">
            <div className="text-sm text-muted-foreground">
              Page {currentPage} sur {usersData.pages} ({usersData.total} utilisateurs)
            </div>
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                disabled={currentPage === 1}
              >
                Précédent
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setCurrentPage(prev => Math.min(usersData.pages, prev + 1))}
                disabled={currentPage === usersData.pages}
              >
                Suivant
              </Button>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default UserManagement;
