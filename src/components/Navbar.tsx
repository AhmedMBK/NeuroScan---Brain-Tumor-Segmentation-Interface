import React, { useState, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Brain, Menu, X, User, LogOut, Settings } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import ThemeSwitcher from '@/components/ThemeSwitcher';
import LanguageSwitcher from '@/components/LanguageSwitcher';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import RoleBasedAccess from '@/components/common/RoleBasedAccess';

const Navbar = () => {
  const { t } = useTranslation();
  const location = useLocation();
  const navigate = useNavigate();
  const { isAuthenticated, userData, logout } = useAuth();
  const [isScrolled, setIsScrolled] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 10);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // Close mobile menu when location changes
  useEffect(() => {
    setIsMobileMenuOpen(false);
  }, [location]);

  return (
    <header
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        isScrolled ? 'bg-white/80 dark:bg-slate-900/80 backdrop-blur-md shadow-sm py-3' : 'bg-transparent py-5'
      }`}
    >
      <div className="container-custom">
        <div className="flex items-center justify-between">
          <Link
            to="/"
            className="flex items-center space-x-2 transition-transform duration-300 hover:scale-[1.02]"
          >
            <Brain className="h-8 w-8 text-medical" strokeWidth={1.5} />
            <span className="text-xl font-semibold text-slate-800 dark:text-white">{t('common.appName')}</span>
          </Link>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center space-x-4">
            {!isAuthenticated ? (
              <>
                <NavLink to="/about" label={t('navigation.about')} />
                <div className="flex items-center space-x-2 ml-4">
                  <ThemeSwitcher />
                  <LanguageSwitcher />
                  <Button asChild variant="outline">
                    <Link to="/login">Se connecter</Link>
                  </Button>
                </div>
              </>
            ) : (
              <>
                <NavLink to="/dashboard" label={t('navigation.dashboard')} />
                <RoleBasedAccess requiredPermissions={['can_view_patients']}>
                  <NavLink to="/patients" label={t('navigation.patients')} />
                </RoleBasedAccess>

                {/* ✅ AJOUTÉ : Navigation pour médecins */}
                <RoleBasedAccess allowedRoles={['DOCTOR']}>
                  <NavLink to="/secretaries" label="Mes Secrétaires" />
                </RoleBasedAccess>

                {/* ✅ AJOUTÉ : Navigation pour secrétaires */}
                <RoleBasedAccess allowedRoles={['SECRETARY']}>
                  <NavLink to="/secretary/appointments" label="Rendez-vous" />
                </RoleBasedAccess>

                <RoleBasedAccess allowedRoles={['ADMIN']}>
                  <NavLink to="/users" label={t('navigation.users')} />
                </RoleBasedAccess>

                <div className="flex items-center space-x-2 ml-4">
                  <ThemeSwitcher />
                  <LanguageSwitcher />

                  {/* Menu utilisateur */}
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button variant="ghost" className="relative h-8 w-8 rounded-full">
                        <Avatar className="h-8 w-8">
                          <AvatarFallback className="bg-medical/10 text-medical">
                            {userData?.first_name?.[0]}{userData?.last_name?.[0]}
                          </AvatarFallback>
                        </Avatar>
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent className="w-56" align="end" forceMount>
                      <DropdownMenuLabel className="font-normal">
                        <div className="flex flex-col space-y-1">
                          <p className="text-sm font-medium leading-none">
                            {userData?.displayName}
                          </p>
                          <p className="text-xs leading-none text-muted-foreground">
                            {userData?.email}
                          </p>
                        </div>
                      </DropdownMenuLabel>
                      <DropdownMenuSeparator />
                      <DropdownMenuItem asChild>
                        <Link to="/settings" className="cursor-pointer">
                          <Settings className="mr-2 h-4 w-4" />
                          <span>Paramètres</span>
                        </Link>
                      </DropdownMenuItem>
                      <DropdownMenuSeparator />
                      <DropdownMenuItem onClick={handleLogout} className="cursor-pointer">
                        <LogOut className="mr-2 h-4 w-4" />
                        <span>Se déconnecter</span>
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </div>
              </>
            )}
          </nav>

          {/* Mobile Menu Button */}
          <div className="flex items-center md:hidden">
            <ThemeSwitcher />
            <LanguageSwitcher />
            <button
              className="p-2 text-slate-700 dark:text-slate-200 focus:outline-none"
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              aria-label="Toggle mobile menu"
            >
              {isMobileMenuOpen ? (
                <X className="h-6 w-6" />
              ) : (
                <Menu className="h-6 w-6" />
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Menu */}
      {isMobileMenuOpen && (
        <div className="md:hidden bg-white dark:bg-slate-800 shadow-lg animate-slide-down">
          <div className="container-custom py-4 flex flex-col space-y-4">
            {!isAuthenticated ? (
              <>
                <NavLink to="/about" label={t('navigation.about')} mobile />
                <Link to="/login" className="block py-2 px-4 rounded-md text-slate-700 dark:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-700">
                  Se connecter
                </Link>
              </>
            ) : (
              <>
                <NavLink to="/dashboard" label={t('navigation.dashboard')} mobile />
                <RoleBasedAccess requiredPermissions={['can_view_patients']}>
                  <NavLink to="/patients" label={t('navigation.patients')} mobile />
                </RoleBasedAccess>

                {/* ✅ AJOUTÉ : Navigation mobile pour médecins */}
                <RoleBasedAccess allowedRoles={['DOCTOR']}>
                  <NavLink to="/secretaries" label="Mes Secrétaires" mobile />
                </RoleBasedAccess>

                {/* ✅ AJOUTÉ : Navigation mobile pour secrétaires */}
                <RoleBasedAccess allowedRoles={['SECRETARY']}>
                  <NavLink to="/secretary/appointments" label="Rendez-vous" mobile />
                </RoleBasedAccess>

                <RoleBasedAccess allowedRoles={['ADMIN']}>
                  <NavLink to="/users" label={t('navigation.users')} mobile />
                </RoleBasedAccess>
                <NavLink to="/settings" label={t('navigation.settings')} mobile />
                <button
                  onClick={handleLogout}
                  className="block py-2 px-4 rounded-md text-slate-700 dark:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-700 text-left"
                >
                  Se déconnecter
                </button>
              </>
            )}
          </div>
        </div>
      )}
    </header>
  );
};

interface NavLinkProps {
  to: string;
  label: string;
  mobile?: boolean;
}

const NavLink = ({ to, label, mobile = false }: NavLinkProps) => {
  const location = useLocation();
  const isActive = location.pathname === to;

  const baseClasses = "transition-all duration-300";
  const mobileClasses = "block py-2 px-4 rounded-md text-slate-700 dark:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-700";
  const desktopClasses = "font-medium hover:text-medical";
  const activeClasses = "text-medical";

  return (
    <Link
      to={to}
      className={`${baseClasses} ${mobile ? mobileClasses : desktopClasses} ${
        isActive ? activeClasses : ""
      }`}
    >
      {label}
    </Link>
  );
};

export default Navbar;
