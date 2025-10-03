import { useLocation } from "react-router-dom";
import { useEffect } from "react";
import { useTranslation } from "react-i18next";

const NotFound = () => {
  const location = useLocation();
  const { t } = useTranslation();

  useEffect(() => {
    console.error(
      "404 Error: User attempted to access non-existent route:",
      location.pathname
    );
  }, [location.pathname]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100 dark:bg-slate-900">
      <div className="text-center">
        <h1 className="text-4xl font-bold mb-4 text-gray-900 dark:text-white">{t('notFound.title')}</h1>
        <p className="text-xl text-gray-600 dark:text-gray-300 mb-4">{t('notFound.message')}</p>
        <a href="/" className="text-medical hover:text-medical-dark dark:text-medical-light dark:hover:text-medical underline">
          {t('notFound.returnHome')}
        </a>
      </div>
    </div>
  );
};

export default NotFound;
