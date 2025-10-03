import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { cerebloomAPI, UserResponse, PaginatedResponse } from '@/services/api';
import { useToast } from '@/hooks/use-toast';

// Hook pour récupérer la liste des utilisateurs
export const useUsers = (page: number = 1, size: number = 10) => {
  return useQuery({
    queryKey: ['users', page, size],
    queryFn: () => cerebloomAPI.getUsers(page, size),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

// Hook pour créer un utilisateur
export const useCreateUser = () => {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: (userData: any) => cerebloomAPI.createUser(userData),
    onSuccess: (newUser) => {
      // Invalider et refetch la liste des utilisateurs
      queryClient.invalidateQueries({ queryKey: ['users'] });

      toast({
        title: "Utilisateur créé",
        description: `${newUser.first_name} ${newUser.last_name} a été créé avec succès`,
      });
    },
    onError: (error: Error) => {
      toast({
        title: "Erreur",
        description: error.message,
        variant: "destructive",
      });
    },
  });
};

// Hook pour modifier un utilisateur
export const useUpdateUser = () => {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: ({ id, userData }: { id: string; userData: any }) =>
      cerebloomAPI.updateUser(id, userData),
    onSuccess: (updatedUser) => {
      // Invalider les queries liées aux utilisateurs
      queryClient.invalidateQueries({ queryKey: ['users'] });

      toast({
        title: "Utilisateur modifié",
        description: `${updatedUser.first_name} ${updatedUser.last_name} a été modifié avec succès`,
      });
    },
    onError: (error: Error) => {
      toast({
        title: "Erreur",
        description: error.message,
        variant: "destructive",
      });
    },
  });
};

// Hook pour supprimer un utilisateur
export const useDeleteUser = () => {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: (userId: string) => cerebloomAPI.deleteUser(userId),
    onSuccess: () => {
      // Invalider et refetch la liste des utilisateurs
      queryClient.invalidateQueries({ queryKey: ['users'] });

      toast({
        title: "Utilisateur supprimé",
        description: "L'utilisateur a été supprimé avec succès",
      });
    },
    onError: (error: Error) => {
      toast({
        title: "Erreur",
        description: error.message,
        variant: "destructive",
      });
    },
  });
};
