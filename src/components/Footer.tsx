
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Brain, Github, Twitter, Linkedin, Mail } from 'lucide-react';

const Footer = () => {
  const { t } = useTranslation();
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-white dark:bg-slate-900 border-t border-slate-200 dark:border-slate-800">
      <div className="container-custom py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div className="md:col-span-2">
            <Link to="/" className="flex items-center space-x-2 mb-4">
              <Brain className="h-6 w-6 text-medical" strokeWidth={1.5} />
              <span className="text-lg font-semibold text-slate-800 dark:text-white">{t('common.appName')}</span>
            </Link>
            <p className="text-slate-600 dark:text-slate-300 mb-6 max-w-md">
              {t('common.footerDescription')}
            </p>
            <div className="flex space-x-4">
              <SocialLink icon={Github} href="#" label="GitHub" />
              <SocialLink icon={Twitter} href="#" label="Twitter" />
              <SocialLink icon={Linkedin} href="#" label="LinkedIn" />
              <SocialLink icon={Mail} href="#" label="Email" />
            </div>
          </div>

          <div>
            <h3 className="font-medium text-slate-800 dark:text-white mb-4">{t('navigation.home')}</h3>
            <ul className="space-y-3">
              <FooterLink to="/" label={t('navigation.home')} />
              <FooterLink to="/#classification-tool" label={t('classification.title')} />
              <FooterLink to="/about" label={t('navigation.about')} />
              <FooterLink to="/login" label={t('common.login')} />
              <FooterLink to="/register" label={t('common.register')} />
            </ul>
          </div>

          <div>
            <h3 className="font-medium text-slate-800 dark:text-white mb-4">{t('navigation.dashboard')}</h3>
            <ul className="space-y-3">
              <FooterLink to="/dashboard" label={t('navigation.dashboard')} />
              <FooterLink to="/patients" label={t('navigation.patients')} />
              <FooterLink to="/settings" label={t('navigation.settings')} />
              <FooterLink to="/users" label={t('navigation.users')} />
            </ul>
          </div>
        </div>

        <div className="mt-12 pt-6 border-t border-slate-100 dark:border-slate-800 text-center">
          <p className="text-slate-500 dark:text-slate-400 text-sm">
            {t('common.copyright', { year: currentYear })}
          </p>
        </div>
      </div>
    </footer>
  );
};

const SocialLink = ({ icon: Icon, href, label }: { icon: any; href: string; label: string }) => {
  return (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      className="w-9 h-9 flex items-center justify-center rounded-full bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-medical hover:text-white transition-colors"
      aria-label={label}
    >
      <Icon className="h-4 w-4" />
    </a>
  );
};

const FooterLink = ({ to, label }: { to: string; label: string }) => {
  return (
    <li>
      <Link to={to} className="text-slate-600 dark:text-slate-300 hover:text-medical dark:hover:text-medical-light transition-colors">
        {label}
      </Link>
    </li>
  );
};

export default Footer;
