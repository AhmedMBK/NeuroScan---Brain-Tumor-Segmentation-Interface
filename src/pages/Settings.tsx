import React from 'react';
import { useTranslation } from 'react-i18next';
import { Moon, Sun, Globe, Bell, Shield, User, Monitor } from 'lucide-react';
import DashboardLayout from '@/components/layouts/DashboardLayout';
import { useTheme } from '@/contexts/ThemeContext';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Switch } from '@/components/ui/switch';
import { Separator } from '@/components/ui/separator';
import { Button } from '@/components/ui/button';
import { useToast } from '@/hooks/use-toast';

const Settings: React.FC = () => {
  const { t, i18n } = useTranslation();
  const { theme, setTheme } = useTheme();
  const { toast } = useToast();

  const handleLanguageChange = (language: string) => {
    i18n.changeLanguage(language);
    localStorage.setItem('i18nextLng', language);
    toast({
      title: t('common.language'),
      description:
        language === 'en'
          ? t('common.english')
          : language === 'fr'
          ? t('common.french')
          : language === 'pt'
          ? t('common.portuguese')
          : language,
    });
  };

  const handleThemeChange = (newTheme: 'light' | 'dark' | 'system') => {
    setTheme(newTheme);
    toast({
      title: t('common.darkMode'),
      description: 
        newTheme === 'light' 
          ? t('common.lightMode') 
          : newTheme === 'dark' 
            ? t('common.darkMode') 
            : 'System',
    });
  };

  return (
    <DashboardLayout>
      <div className="p-6">
        <div className="mb-6">
          <h1 className="text-3xl font-bold tracking-tight">{t('navigation.settings')}</h1>
          <p className="text-muted-foreground">
            {t('navigation.settings')}
          </p>
        </div>

        <div className="grid gap-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Globe className="mr-2 h-5 w-5 text-medical" />
                {t('common.language')}
              </CardTitle>
              <CardDescription>
                Choose your preferred language for the application interface.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <RadioGroup 
                defaultValue={i18n.language} 
                onValueChange={handleLanguageChange}
                className="flex flex-col space-y-3"
              >
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="en" id="en" />
                  <Label htmlFor="en" className="cursor-pointer">
                    {t('common.english')}
                  </Label>
                </div>
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="fr" id="fr" />
                  <Label htmlFor="fr" className="cursor-pointer">
                    {t('common.french')}
                  </Label>
                </div>
              </RadioGroup>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Moon className="mr-2 h-5 w-5 text-medical" />
                {t('common.darkMode')}
              </CardTitle>
              <CardDescription>
                Choose your preferred theme for the application interface.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <RadioGroup 
                defaultValue={theme} 
                onValueChange={(value) => handleThemeChange(value as 'light' | 'dark' | 'system')}
                className="flex flex-col space-y-3"
              >
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="light" id="light" />
                  <Label htmlFor="light" className="flex items-center cursor-pointer">
                    <Sun className="mr-2 h-4 w-4" />
                    {t('common.lightMode')}
                  </Label>
                </div>
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="dark" id="dark" />
                  <Label htmlFor="dark" className="flex items-center cursor-pointer">
                    <Moon className="mr-2 h-4 w-4" />
                    {t('common.darkMode')}
                  </Label>
                </div>
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="system" id="system" />
                  <Label htmlFor="system" className="flex items-center cursor-pointer">
                    <Monitor className="mr-2 h-4 w-4" />
                    System
                  </Label>
                </div>
              </RadioGroup>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Bell className="mr-2 h-5 w-5 text-medical" />
                Notifications
              </CardTitle>
              <CardDescription>
                Configure your notification preferences.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <Label htmlFor="email-notifications" className="block">Email Notifications</Label>
                    <p className="text-sm text-muted-foreground">
                      Receive email notifications for important updates.
                    </p>
                  </div>
                  <Switch id="email-notifications" defaultChecked />
                </div>
                <Separator />
                <div className="flex items-center justify-between">
                  <div>
                    <Label htmlFor="browser-notifications" className="block">Browser Notifications</Label>
                    <p className="text-sm text-muted-foreground">
                      Receive browser notifications when using the application.
                    </p>
                  </div>
                  <Switch id="browser-notifications" defaultChecked />
                </div>
                <Separator />
                <div className="flex items-center justify-between">
                  <div>
                    <Label htmlFor="scan-notifications" className="block">Scan Completion Notifications</Label>
                    <p className="text-sm text-muted-foreground">
                      Get notified when a scan analysis is complete.
                    </p>
                  </div>
                  <Switch id="scan-notifications" defaultChecked />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Shield className="mr-2 h-5 w-5 text-medical" />
                Security
              </CardTitle>
              <CardDescription>
                Manage your account security settings.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <Label htmlFor="two-factor" className="block">Two-Factor Authentication</Label>
                    <p className="text-sm text-muted-foreground">
                      Add an extra layer of security to your account.
                    </p>
                  </div>
                  <Switch id="two-factor" />
                </div>
                <Separator />
                <div>
                  <Button variant="outline">Change Password</Button>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <User className="mr-2 h-5 w-5 text-medical" />
                Account
              </CardTitle>
              <CardDescription>
                Manage your account settings.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <Button variant="outline">Edit Profile</Button>
                </div>
                <Separator />
                <div>
                  <Button variant="destructive">Delete Account</Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </DashboardLayout>
  );
};

export default Settings;
