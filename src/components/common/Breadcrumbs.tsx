import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { ChevronRight, Home } from 'lucide-react';

interface BreadcrumbItem {
  label: string;
  href?: string;
  active?: boolean;
}

interface BreadcrumbsProps {
  items?: BreadcrumbItem[];
  className?: string;
}

const Breadcrumbs: React.FC<BreadcrumbsProps> = ({ items, className = '' }) => {
  const location = useLocation();

  // Générer automatiquement les breadcrumbs si pas fournis
  const generateBreadcrumbs = (): BreadcrumbItem[] => {
    const pathSegments = location.pathname.split('/').filter(Boolean);
    const breadcrumbs: BreadcrumbItem[] = [
      { label: 'Accueil', href: '/dashboard' }
    ];

    let currentPath = '';

    pathSegments.forEach((segment, index) => {
      currentPath += `/${segment}`;
      const isLast = index === pathSegments.length - 1;

      // Mapper les segments vers des labels lisibles
      let label = segment;
      switch (segment) {
        case 'dashboard':
          label = 'Tableau de bord';
          break;
        case 'patients':
          label = 'Patients';
          break;
        case 'doctors':
          label = 'Médecins';
          break;
        case 'reports':
          label = 'Rapports';
          break;
        case 'users':
          label = 'Administration';
          break;
        case 'settings':
          label = 'Paramètres';
          break;
        case 'new':
          label = 'Nouveau';
          break;
        case 'edit':
          label = 'Modifier';
          break;
        case 'upload':
          label = 'Upload Images';
          break;
        case 'exam-history':
          label = 'Historique Examens';
          break;
        case 'treatment-tracking':
          label = 'Suivi Traitements';
          break;
        default:
          // Si c'est un ID (UUID ou nombre), essayer de le raccourcir
          if (segment.match(/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i)) {
            label = `Patient ${segment.substring(0, 8)}...`;
          } else if (segment.match(/^\d+$/)) {
            label = `ID ${segment}`;
          }
          break;
      }

      breadcrumbs.push({
        label,
        href: isLast ? undefined : currentPath,
        active: isLast
      });
    });

    return breadcrumbs;
  };

  const breadcrumbItems = items || generateBreadcrumbs();

  return (
    <nav className={`flex items-center space-x-1 text-sm text-muted-foreground ${className}`}>
      <Home className="h-4 w-4" />
      {breadcrumbItems.map((item, index) => (
        <span key={index} className="flex items-center space-x-1">
          {index > 0 && <ChevronRight className="h-4 w-4" />}
          {item.href && !item.active ? (
            <Link
              to={item.href}
              className="hover:text-foreground transition-colors"
            >
              {item.label}
            </Link>
          ) : (
            <span className={item.active ? 'text-foreground font-medium' : ''}>
              {item.label}
            </span>
          )}
        </span>
      ))}
    </nav>
  );
};

export default Breadcrumbs;
