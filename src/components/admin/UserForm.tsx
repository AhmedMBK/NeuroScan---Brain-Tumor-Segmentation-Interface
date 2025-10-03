import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Checkbox } from '@/components/ui/checkbox';

// Schéma de validation
const userSchema = z.object({
  first_name: z.string().min(2, 'Le prénom doit contenir au moins 2 caractères'),
  last_name: z.string().min(2, 'Le nom doit contenir au moins 2 caractères'),
  email: z.string().email('Email invalide'),
  username: z.string().min(3, 'Le nom d\'utilisateur doit contenir au moins 3 caractères'),
  role: z.enum(['ADMIN', 'DOCTOR', 'SECRETARY'], {
    required_error: 'Le rôle est requis',
  }),
  employee_id: z.string().optional(),
  password: z.string().min(8, 'Le mot de passe doit contenir au moins 8 caractères').optional(),
  confirm_password: z.string().optional(),
  is_active: z.boolean().default(true),
}).refine((data) => {
  if (data.password && data.confirm_password) {
    return data.password === data.confirm_password;
  }
  return true;
}, {
  message: "Les mots de passe ne correspondent pas",
  path: ["confirm_password"],
});

type UserFormData = z.infer<typeof userSchema>;

interface UserFormProps {
  mode: 'create' | 'edit';
  initialData?: Partial<any>;
  onSubmit: (data: UserFormData) => void;
  onCancel: () => void;
  isLoading?: boolean;
}

const UserForm: React.FC<UserFormProps> = ({
  mode,
  initialData,
  onSubmit,
  onCancel,
  isLoading = false,
}) => {
  const form = useForm<UserFormData>({
    resolver: zodResolver(userSchema),
    defaultValues: {
      first_name: initialData?.first_name || '',
      last_name: initialData?.last_name || '',
      email: initialData?.email || '',
      username: initialData?.username || '',
      role: initialData?.role || undefined,
      employee_id: initialData?.employee_id || '',
      password: '',
      confirm_password: '',
      is_active: initialData?.is_active !== false,
    },
  });



  const handleSubmit = (data: UserFormData) => {
    // Nettoyer les données avant envoi
    const cleanedData = {
      ...data,
      employee_id: data.employee_id || undefined,
      password: data.password || undefined,
      confirm_password: undefined, // Ne pas envoyer la confirmation
    };

    onSubmit(cleanedData);
  };



  return (
    <Card className="w-full max-w-4xl mx-auto">
      <CardHeader>
        <CardTitle>
          {mode === 'create' ? 'Nouvel Utilisateur' : 'Modifier Utilisateur'}
        </CardTitle>
        <CardDescription>
          {mode === 'create'
            ? 'Créer un nouveau compte utilisateur dans le système'
            : 'Modifier les informations et permissions de l\'utilisateur'
          }
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-6">
            {/* Informations personnelles */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name="first_name"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Prénom *</FormLabel>
                    <FormControl>
                      <Input placeholder="Jean" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="last_name"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Nom *</FormLabel>
                    <FormControl>
                      <Input placeholder="Dupont" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="email"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Email *</FormLabel>
                    <FormControl>
                      <Input type="email" placeholder="jean.dupont@cerebloom.com" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="username"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Nom d'utilisateur *</FormLabel>
                    <FormControl>
                      <Input placeholder="jean.dupont" {...field} />
                    </FormControl>
                    <FormDescription>
                      Identifiant unique pour la connexion (minimum 3 caractères)
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="employee_id"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>ID Employé</FormLabel>
                    <FormControl>
                      <Input
                        placeholder="Auto-généré selon le rôle (DOC001, SEC001, ADM001)"
                        {...field}
                      />
                    </FormControl>
                    <FormDescription>
                      ✨ Laissez vide pour génération automatique selon le rôle sélectionné
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            {/* Rôle et statut */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name="role"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Rôle *</FormLabel>
                    <Select onValueChange={field.onChange} defaultValue={field.value}>
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Sélectionner un rôle" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        <SelectItem value="ADMIN">Administrateur</SelectItem>
                        <SelectItem value="DOCTOR">Médecin</SelectItem>
                        <SelectItem value="SECRETARY">Secrétaire</SelectItem>
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="is_active"
                render={({ field }) => (
                  <FormItem className="flex flex-row items-start space-x-3 space-y-0 rounded-md border p-4">
                    <FormControl>
                      <Checkbox
                        checked={field.value}
                        onCheckedChange={field.onChange}
                      />
                    </FormControl>
                    <div className="space-y-1 leading-none">
                      <FormLabel>
                        Compte actif
                      </FormLabel>
                      <FormDescription>
                        L'utilisateur peut se connecter au système
                      </FormDescription>
                    </div>
                  </FormItem>
                )}
              />
            </div>

            {/* Mot de passe (seulement en création ou si modification demandée) */}
            {mode === 'create' && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <FormField
                  control={form.control}
                  name="password"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Mot de passe *</FormLabel>
                      <FormControl>
                        <Input type="password" placeholder="••••••••" {...field} />
                      </FormControl>
                      <FormDescription>
                        Minimum 8 caractères
                      </FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="confirm_password"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Confirmer le mot de passe *</FormLabel>
                      <FormControl>
                        <Input type="password" placeholder="••••••••" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>
            )}

            {/* Actions */}
            <div className="flex justify-end space-x-4 pt-6">
              <Button
                type="button"
                variant="outline"
                onClick={onCancel}
                disabled={isLoading}
              >
                Annuler
              </Button>
              <Button type="submit" disabled={isLoading}>
                {isLoading ? 'Enregistrement...' : mode === 'create' ? 'Créer' : 'Modifier'}
              </Button>
            </div>
          </form>
        </Form>
      </CardContent>
    </Card>
  );
};

export default UserForm;
