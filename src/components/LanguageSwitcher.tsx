import React from 'react';
import { useTranslation } from 'react-i18next';
import { Globe } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';

const LanguageSwitcher: React.FC = () => {
  const { i18n, t } = useTranslation();

  const changeLanguage = (language: string) => {
    i18n.changeLanguage(language);
    // Store the language preference
    localStorage.setItem('i18nextLng', language);
  };

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon" className="h-9 w-9 rounded-full">
          <Globe className="h-4 w-4" />
          <span className="sr-only">{t('common.language')}</span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuItem onClick={() => changeLanguage('en')}>
          {t('common.english')}
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => changeLanguage('fr')}>
          {t('common.french')}
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => changeLanguage('pt')}>
          {t('common.portuguese')}
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
};

export default LanguageSwitcher;
