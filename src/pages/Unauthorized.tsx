import React from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { ShieldAlert, ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';

const Unauthorized: React.FC = () => {
  const { t } = useTranslation();

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-slate-50 dark:bg-slate-900 p-4">
      <div className="text-center max-w-md">
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-red-100 mb-6">
          <ShieldAlert className="h-8 w-8 text-red-600" />
        </div>
        
        <h1 className="text-3xl font-bold text-slate-900 dark:text-white mb-2">
          {t('auth.unauthorized')}
        </h1>
        
        <p className="text-slate-600 dark:text-slate-400 mb-8">
          {t('auth.unauthorizedMessage')}
        </p>
        
        <div className="flex flex-col space-y-4">
          <Button asChild>
            <Link to="/dashboard">
              <ArrowLeft className="mr-2 h-4 w-4" />
              {t('navigation.dashboard')}
            </Link>
          </Button>
          
          <Button variant="outline" asChild>
            <Link to="/">
              {t('navigation.home')}
            </Link>
          </Button>
        </div>
      </div>
    </div>
  );
};

export default Unauthorized;
