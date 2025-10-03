import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Loader2, UserPlus, AlertCircle } from 'lucide-react';
import { useCreateSecretary } from '@/hooks/api/useSecretaries';

// Schéma de validation
const createSecretarySchema = z.object({
  first_name: z.string().min(2, 'Le prénom doit contenir au moins 2 caractères'),
  last_name: z.string().min(2, 'Le nom doit contenir au moins 2 caractères'),
  email: z.string().email('Adresse email invalide'),
  username: z.string().min(3, 'Le nom d\'utilisateur doit contenir au moins 3 caractères'),
  password: z.string().min(6, 'Le mot de passe doit contenir au moins 6 caractères'),
  phone: z.string().optional(),
});

type CreateSecretaryFormData = z.infer<typeof createSecretarySchema>;

interface CreateSecretaryFormProps {
  onSuccess: () => void;
}

const CreateSecretaryForm: React.FC<CreateSecretaryFormProps> = ({ onSuccess }) => {
  const createSecretaryMutation = useCreateSecretary();

  const form = useForm<CreateSecretaryFormData>({
    resolver: zodResolver(createSecretarySchema),
    defaultValues: {
      first_name: '',
      last_name: '',
      email: '',
      username: '',
      password: '',
      phone: '',
    },
  });

  const onSubmit = async (data: CreateSecretaryFormData) => {
    try {
      await createSecretaryMutation.mutateAsync(data);
      onSuccess();
    } catch (error) {
      console.error('Erreur lors de la création de la secrétaire:', error);
    }
  };

  return (
    <div className="space-y-6">
      {/* Alerte d'information */}
      <Alert className="border-blue-200 bg-blue-50">
        <UserPlus className="h-4 w-4 text-blue-600" />
        <AlertDescription className="text-blue-800">
          La secrétaire sera automatiquement assignée à votre cabinet médical et aura accès aux patients qui vous sont assignés.
        </AlertDescription>
      </Alert>

      {/* Affichage des erreurs */}
      {createSecretaryMutation.isError && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            {createSecretaryMutation.error?.message || 'Erreur lors de la création de la secrétaire'}
          </AlertDescription>
        </Alert>
      )}

      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
          {/* Informations personnelles */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <FormField
              control={form.control}
              name="first_name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Prénom *</FormLabel>
                  <FormControl>
                    <Input placeholder="Marie" {...field} />
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
          </div>

          {/* Contact */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <FormField
              control={form.control}
              name="email"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Email *</FormLabel>
                  <FormControl>
                    <Input type="email" placeholder="marie.dupont@cabinet.com" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="phone"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Téléphone</FormLabel>
                  <FormControl>
                    <Input placeholder="+33 1 23 45 67 89" {...field} />
                  </FormControl>
                  <FormDescription>
                    Numéro de téléphone professionnel (optionnel)
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />
          </div>

          {/* Identifiants de connexion */}
          <div className="border-t pt-4">
            <h4 className="font-medium mb-4 text-lg">Identifiants de connexion</h4>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name="username"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Nom d'utilisateur *</FormLabel>
                    <FormControl>
                      <Input placeholder="marie.dupont" {...field} />
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
                name="password"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Mot de passe *</FormLabel>
                    <FormControl>
                      <Input type="password" placeholder="••••••••" {...field} />
                    </FormControl>
                    <FormDescription>
                      Minimum 6 caractères. La secrétaire pourra le modifier après la première connexion.
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>
          </div>

          {/* Boutons d'action */}
          <div className="flex justify-end gap-3 pt-6 border-t">
            <Button
              type="button"
              variant="outline"
              onClick={() => form.reset()}
              disabled={createSecretaryMutation.isPending}
              size="lg"
            >
              Réinitialiser
            </Button>
            <Button
              type="submit"
              disabled={createSecretaryMutation.isPending}
              className="min-w-[160px]"
              size="lg"
            >
              {createSecretaryMutation.isPending ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Création en cours...
                </>
              ) : (
                <>
                  <UserPlus className="mr-2 h-4 w-4" />
                  Créer la secrétaire
                </>
              )}
            </Button>
          </div>
        </form>
      </Form>

      {/* Message de succès */}
      {createSecretaryMutation.isSuccess && (
        <Alert className="border-green-200 bg-green-50">
          <UserPlus className="h-4 w-4 text-green-600" />
          <AlertDescription className="text-green-800">
            Secrétaire créée avec succès ! Elle peut maintenant se connecter avec ses identifiants.
          </AlertDescription>
        </Alert>
      )}
    </div>
  );
};

export default CreateSecretaryForm;
