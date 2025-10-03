import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { Brain, Mail, Lock, Loader2 } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { useToast } from '@/hooks/use-toast';
import ThemeSwitcher from '@/components/ThemeSwitcher';
import LanguageSwitcher from '@/components/LanguageSwitcher';

// Define form schema with Zod
const loginSchema = z.object({
  email: z.string().email(),
  password: z.string().min(6, 'Password must be at least 6 characters'),
});

type LoginFormValues = z.infer<typeof loginSchema>;

const Login: React.FC = () => {
  const { t } = useTranslation();
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const { toast } = useToast();
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  // Get the redirect path from location state or default to dashboard
  const from = (location.state as any)?.from?.pathname || '/dashboard';

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: 'admin@cerebloom.com',
      password: 'admin123',
    },
  });

  const onSubmit = async (data: LoginFormValues) => {
    setIsLoading(true);
    setError(null);

    try {
      await login(data.email, data.password);
      toast({
        title: t('auth.loginSuccess'),
        description: t('auth.loginSuccess'),
      });
      navigate(from, { replace: true });
    } catch (err: any) {
      setError(t('auth.loginError'));
      toast({
        variant: 'destructive',
        title: t('auth.loginError'),
        description: err.message,
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50 dark:bg-slate-900 p-4">
      <div className="absolute top-4 right-4 flex items-center space-x-2">
        <ThemeSwitcher />
        <LanguageSwitcher />
      </div>

      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-medical/10 mb-4">
            <Brain className="h-8 w-8 text-medical" strokeWidth={1.5} />
          </div>
          <h1 className="text-3xl font-bold text-slate-900 dark:text-white">{t('common.appName')}</h1>
        </div>

        <Card className="w-full">
          <CardHeader>
            <CardTitle>{t('auth.loginTitle')}</CardTitle>
            <CardDescription>{t('auth.loginSubtitle')}</CardDescription>
          </CardHeader>
          <CardContent>
            {error && (
              <Alert variant="destructive" className="mb-4">
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="email">{t('common.email')}</Label>
                <div className="relative">
                  <Mail className="absolute left-3 top-3 h-4 w-4 text-slate-400" />
                  <Input
                    id="email"
                    type="email"
                    placeholder="name@example.com"
                    className="pl-10"
                    {...register('email')}
                  />
                </div>
                {errors.email && (
                  <p className="text-sm text-red-500">{errors.email.message}</p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="password">{t('common.password')}</Label>
                <div className="relative">
                  <Lock className="absolute left-3 top-3 h-4 w-4 text-slate-400" />
                  <Input
                    id="password"
                    type="password"
                    className="pl-10"
                    {...register('password')}
                  />
                </div>
                {errors.password && (
                  <p className="text-sm text-red-500">{errors.password.message}</p>
                )}
              </div>

              <Button type="submit" className="w-full" disabled={isLoading}>
                {isLoading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    {t('common.loading')}
                  </>
                ) : (
                  t('common.login')
                )}
              </Button>
            </form>
          </CardContent>
          <CardFooter className="flex justify-center">
            <p className="text-sm text-slate-600 dark:text-slate-400">
              Besoin d'un compte ? Contactez votre administrateur système.
            </p>
          </CardFooter>
        </Card>
      </div>
    </div>
  );
};

export default Login;
