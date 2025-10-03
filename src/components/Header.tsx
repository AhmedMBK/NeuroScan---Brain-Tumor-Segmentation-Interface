
import { useState, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Menu, X, Brain, LogOut, User, Settings } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import ThemeSwitcher from '@/components/ThemeSwitcher';
import LanguageSwitcher from '@/components/LanguageSwitcher';
import { useToast } from '@/hooks/use-toast';

const Header = () => {
  const { t } = useTranslation();
  const { currentUser, userData, logout } = useAuth();
  const [isScrolled, setIsScrolled] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const { toast } = useToast();

  const isAuthenticated = !!currentUser;
  const displayName = currentUser?.displayName || userData?.displayName || '';
  const initials = displayName
    .split(' ')
    .map(name => name?.[0] || '')
    .join('')
    .toUpperCase();

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 10);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  useEffect(() => {
    setIsMobileMenuOpen(false);
  }, [location]);

  const handleLogout = async () => {
    try {
      await logout();
      toast({
        title: t('auth.logoutSuccess'),
        description: t('auth.logoutSuccess'),
      });
      navigate('/login');
    } catch (error) {
      console.error('Logout error:', error);
      toast({
        variant: 'destructive',
        title: t('common.error'),
        description: String(error),
      });
    }
  };

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
            <NavLink to="/" label={t('navigation.home')} />
            <NavLink to="/about" label={t('navigation.about')} />

            {isAuthenticated ? (
              <>
                <NavLink to="/dashboard" label={t('navigation.dashboard')} />
                <div className="flex items-center space-x-2 ml-4">
                  <ThemeSwitcher />
                  <LanguageSwitcher />

                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button variant="ghost" className="relative h-8 w-8 rounded-full">
                        <Avatar className="h-8 w-8">
                          <AvatarFallback className="bg-medical/10 text-medical">
                            {initials || 'U'}
                          </AvatarFallback>
                        </Avatar>
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      <DropdownMenuLabel>{displayName}</DropdownMenuLabel>
                      <DropdownMenuSeparator />
                      <DropdownMenuItem asChild>
                        <Link to="/dashboard" className="flex items-center">
                          <User className="mr-2 h-4 w-4" />
                          <span>{t('navigation.dashboard')}</span>
                        </Link>
                      </DropdownMenuItem>
                      <DropdownMenuItem asChild>
                        <Link to="/settings" className="flex items-center">
                          <Settings className="mr-2 h-4 w-4" />
                          <span>{t('navigation.settings')}</span>
                        </Link>
                      </DropdownMenuItem>
                      <DropdownMenuSeparator />
                      <DropdownMenuItem
                        className="text-red-500 focus:text-red-500"
                        onClick={handleLogout}
                      >
                        <LogOut className="mr-2 h-4 w-4" />
                        <span>{t('common.logout')}</span>
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </div>
              </>
            ) : (
              <div className="flex items-center space-x-2 ml-4">
                <ThemeSwitcher />
                <LanguageSwitcher />
                <Button variant="ghost" asChild>
                  <Link to="/login">{t('common.login')}</Link>
                </Button>
                <Button asChild>
                  <Link to="/register">{t('common.register')}</Link>
                </Button>
              </div>
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
            <NavLink to="/" label={t('navigation.home')} mobile />
            <NavLink to="/about" label={t('navigation.about')} mobile />

            {isAuthenticated ? (
              <>
                <NavLink to="/dashboard" label={t('navigation.dashboard')} mobile />
                <NavLink to="/patients" label={t('navigation.patients')} mobile />
                <NavLink to="/settings" label={t('navigation.settings')} mobile />
                {userData?.role === 'admin' && (
                  <NavLink to="/users" label={t('navigation.users')} mobile />
                )}
                <button
                  onClick={handleLogout}
                  className="py-2 px-4 text-left text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-md transition-colors"
                >
                  {t('common.logout')}
                </button>
              </>
            ) : (
              <div className="flex flex-col space-y-2 pt-2">
                <Button variant="outline" asChild className="w-full justify-center">
                  <Link to="/login">{t('common.login')}</Link>
                </Button>
                <Button asChild className="w-full justify-center">
                  <Link to="/register">{t('common.register')}</Link>
                </Button>
              </div>
            )}
          </div>
        </div>
      )}
    </header>
  );
};

const NavLink = ({ to, label, mobile = false }: { to: string; label: string; mobile?: boolean }) => {
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

export default Header;
