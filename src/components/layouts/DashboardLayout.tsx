import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  Users,
  FileText,
  Settings,
  ChevronDown,
  ChevronRight,
  UserCircle,
  PlusCircle,
  Search,
  Pencil as PencilIcon,
  FileImage as FileImageIcon,
  Activity as ActivityIcon,
  Stethoscope,
  BarChart3,
  Shield
} from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import RoleBasedAccess from '@/components/common/RoleBasedAccess';
import Breadcrumbs from '@/components/common/Breadcrumbs';

interface DashboardLayoutProps {
  children: React.ReactNode;
}

interface NavItemProps {
  to: string;
  icon: React.ReactNode;
  label: string;
  active?: boolean;
  onClick?: () => void;
  subItems?: Array<{
    to: string;
    icon: React.ReactNode;
    label: string;
    active?: boolean;
  }>;
}

const NavItem: React.FC<NavItemProps> = ({ to, icon, label, active, onClick, subItems }) => {
  // Check if any subItem is active to auto-expand the menu
  const hasActiveSubItem = subItems?.some(item => item.active) || false;
  const [isOpen, setIsOpen] = useState(hasActiveSubItem);
  const hasSubItems = subItems && subItems.length > 0;

  const toggleSubMenu = (e: React.MouseEvent) => {
    if (hasSubItems) {
      e.preventDefault();
      setIsOpen(!isOpen);
    }
  };

  return (
    <div className="flex flex-col">
      <Link
        to={hasSubItems ? '#' : to}
        className={`flex items-center justify-between px-3 py-2 rounded-md transition-colors ${
          active
            ? 'bg-medical/10 text-medical'
            : 'text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800'
        }`}
        onClick={hasSubItems ? toggleSubMenu : onClick}
      >
        <div className="flex items-center gap-3">
          {icon}
          <span>{label}</span>
        </div>
        {hasSubItems && (
          isOpen ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />
        )}
      </Link>

      {hasSubItems && isOpen && (
        <div className="ml-6 mt-1 border-l-2 border-slate-200 dark:border-slate-700 pl-2 space-y-1">
          {subItems.map((item, index) => (
            <Link
              key={index}
              to={item.to}
              className={`flex items-center gap-3 px-3 py-2 rounded-md transition-colors text-sm ${
                item.active
                  ? 'bg-medical/10 text-medical'
                  : 'text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800'
              }`}
            >
              {item.icon}
              <span>{item.label}</span>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
};

const DashboardLayout: React.FC<DashboardLayoutProps> = ({ children }) => {
  const { t } = useTranslation();
  const location = useLocation();
  const { userData } = useAuth();

  // Get patient ID from URL if we're on a patient detail page or any sub-page
  const patientIdMatch = location.pathname.match(/\/patients\/([^/]+)(\/.*)?$/);
  const currentPatientId = patientIdMatch ? patientIdMatch[1] : null;

  // Check if we're on the patient detail page specifically
  const isPatientDetailPage = location.pathname === `/patients/${currentPatientId}`;

  // Navigation items avec contrôles de rôles
  const allNavItems = [
    {
      to: '/dashboard',
      icon: <LayoutDashboard className="h-5 w-5" />,
      label: t('navigation.dashboard'),
      active: location.pathname === '/dashboard',
      roles: ['ADMIN', 'DOCTOR', 'SECRETARY'], // Accessible à tous
    },
    {
      to: '/patients',
      icon: <FileText className="h-5 w-5" />,
      label: t('navigation.patients'),
      active: location.pathname.startsWith('/patients'),
      roles: ['ADMIN', 'DOCTOR', 'SECRETARY'], // Accessible à tous
      subItems: [
        {
          to: '/patients',
          icon: <Users className="h-4 w-4" />,
          label: t('patients.patientList'),
          active: location.pathname === '/patients',
          roles: ['ADMIN', 'DOCTOR', 'SECRETARY'],
        },
        {
          to: '/patients/new',
          icon: <PlusCircle className="h-4 w-4" />,
          label: t('patients.addPatient'),
          active: location.pathname === '/patients/new',
          roles: ['ADMIN', 'DOCTOR', 'SECRETARY'],
        },
        ...(currentPatientId ? [
          {
            to: `/patients/${currentPatientId}`,
            icon: <UserCircle className="h-4 w-4" />,
            label: t('patients.patientDetails'),
            active: isPatientDetailPage,
            roles: ['ADMIN', 'DOCTOR', 'SECRETARY'],
          },
          {
            to: `/patients/${currentPatientId}/edit`,
            icon: <PencilIcon className="h-4 w-4" />,
            label: t('patients.editPatient'),
            active: location.pathname === `/patients/${currentPatientId}/edit`,
            roles: ['ADMIN', 'DOCTOR', 'SECRETARY'],
          },
          {
            to: `/patients/${currentPatientId}/exam-history`,
            icon: <FileImageIcon className="h-4 w-4" />,
            label: t('scans.examHistory'),
            active: location.pathname === `/patients/${currentPatientId}/exam-history`,
            roles: ['ADMIN', 'DOCTOR', 'SECRETARY'],
          },
          {
            to: `/patients/${currentPatientId}/treatment-tracking`,
            icon: <ActivityIcon className="h-4 w-4" />,
            label: t('treatments.treatmentTracking'),
            active: location.pathname === `/patients/${currentPatientId}/treatment-tracking`,
            roles: ['ADMIN', 'DOCTOR'],
          }
        ] : []),
      ],
    },
    {
      to: '/doctors',
      icon: <Stethoscope className="h-5 w-5" />,
      label: t('navigation.doctors'),
      active: location.pathname.startsWith('/doctors'),
      roles: ['ADMIN'], // Seulement ADMIN
    },
    {
      to: '/users',
      icon: <Shield className="h-5 w-5" />,
      label: t('navigation.users'),
      active: location.pathname.startsWith('/users'),
      roles: ['ADMIN'], // Seulement ADMIN
    },
    {
      to: '/reports',
      icon: <BarChart3 className="h-5 w-5" />,
      label: 'Rapports',
      active: location.pathname.startsWith('/reports'),
      roles: ['ADMIN', 'DOCTOR'], // ADMIN et DOCTOR
    },
    {
      to: '/settings',
      icon: <Settings className="h-5 w-5" />,
      label: t('navigation.settings'),
      active: location.pathname === '/settings',
      roles: ['ADMIN', 'DOCTOR', 'SECRETARY'], // Accessible à tous
    },
  ];

  // Filtrer les items selon le rôle de l'utilisateur
  const navItems = allNavItems.filter(item =>
    item.roles.includes(userData?.role || 'SECRETARY')
  ).map(item => ({
    ...item,
    subItems: item.subItems?.filter(subItem =>
      subItem.roles.includes(userData?.role || 'SECRETARY')
    )
  }));

  return (
    <div className="flex flex-1">
      {/* Sidebar */}
      <aside className="hidden md:flex w-64 flex-col border-r bg-background">
        <nav className="flex-1 overflow-auto p-4">
          <div className="flex flex-col gap-1">
            {navItems.map((item, index) => (
              <NavItem
                key={index}
                to={item.to}
                icon={item.icon}
                label={item.label}
                active={item.active}
                subItems={item.subItems}
              />
            ))}
          </div>
        </nav>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-auto">
        {/* Breadcrumbs */}
        <div className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
          <div className="p-4">
            <Breadcrumbs />
          </div>
        </div>
        {children}
      </main>
    </div>
  );
};

export default DashboardLayout;
