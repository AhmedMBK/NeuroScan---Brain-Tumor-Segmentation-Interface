import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import DashboardLayout from '@/components/layouts/DashboardLayout';
import UserManagement from '@/components/admin/UserManagement';
import UserForm from '@/components/admin/UserForm';
import { useCreateUser, useUpdateUser } from '@/hooks/api/useUsers';
import RoleBasedAccess from '@/components/common/RoleBasedAccess';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';

type ViewMode = 'list' | 'create' | 'edit';

const Users: React.FC = () => {
  const navigate = useNavigate();
  const [viewMode, setViewMode] = useState<ViewMode>('list');
  const [selectedUserId, setSelectedUserId] = useState<string | null>(null);
  const [isDialogOpen, setIsDialogOpen] = useState(false);

  // Hooks API
  const createUserMutation = useCreateUser();
  const updateUserMutation = useUpdateUser();

  // Gestion de la création d'utilisateur
  const handleCreateUser = () => {
    setViewMode('create');
    setSelectedUserId(null);
    setIsDialogOpen(true);
  };

  // Gestion de l'édition d'utilisateur
  const handleEditUser = (userId: string) => {
    setViewMode('edit');
    setSelectedUserId(userId);
    setIsDialogOpen(true);
  };

  // Soumission du formulaire
  const handleFormSubmit = async (data: any) => {
    try {
      if (viewMode === 'create') {
        await createUserMutation.mutateAsync(data);
      } else if (viewMode === 'edit' && selectedUserId) {
        await updateUserMutation.mutateAsync({
          id: selectedUserId,
          userData: data
        });
      }

      // Fermer le dialog et revenir à la liste
      setIsDialogOpen(false);
      setViewMode('list');
      setSelectedUserId(null);
    } catch (error) {
      console.error('Erreur lors de la soumission:', error);
    }
  };

  // Annulation du formulaire
  const handleFormCancel = () => {
    setIsDialogOpen(false);
    setViewMode('list');
    setSelectedUserId(null);
  };

  return (
    <RoleBasedAccess
      allowedRoles={['ADMIN']}
      fallback={
        <DashboardLayout>
          <div className="p-6">
            <div className="text-center">
              <h1 className="text-2xl font-bold text-destructive">Accès refusé</h1>
              <p className="text-muted-foreground mt-2">
                Vous n'avez pas les permissions nécessaires pour gérer les utilisateurs.
              </p>
              <Button
                variant="outline"
                onClick={() => navigate('/dashboard')}
                className="mt-4"
              >
                Retour au tableau de bord
              </Button>
            </div>
          </div>
        </DashboardLayout>
      }
    >
      <DashboardLayout>
        <div className="p-6">
          {/* Header */}
          <div className="mb-6">
            <h1 className="text-2xl font-bold tracking-tight">Administration</h1>
            <p className="text-muted-foreground">
              Gestion des utilisateurs, permissions et accès au système CereBloom
            </p>
          </div>

          {/* Contenu principal */}
          <UserManagement
            onCreateUser={handleCreateUser}
            onEditUser={handleEditUser}
          />

          {/* Dialog pour création/édition */}
          <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
            <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
              <DialogHeader>
                <DialogTitle>
                  {viewMode === 'create' ? 'Nouvel Utilisateur' : 'Modifier Utilisateur'}
                </DialogTitle>
                <DialogDescription>
                  {viewMode === 'create'
                    ? 'Créer un nouveau compte utilisateur dans le système CereBloom'
                    : 'Modifier les informations et permissions de l\'utilisateur'
                  }
                </DialogDescription>
              </DialogHeader>

              <UserForm
                mode={viewMode === 'create' ? 'create' : 'edit'}
                initialData={selectedUserId ? { id: selectedUserId } : undefined}
                onSubmit={handleFormSubmit}
                onCancel={handleFormCancel}
                isLoading={createUserMutation.isPending || updateUserMutation.isPending}
              />
            </DialogContent>
          </Dialog>
        </div>
      </DashboardLayout>
    </RoleBasedAccess>
  );
};

export default Users;
