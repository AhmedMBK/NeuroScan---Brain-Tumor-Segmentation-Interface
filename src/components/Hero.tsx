
import { ChevronRight, Microscope, Brain, Dna } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

const Hero = () => {
  const { t } = useTranslation();
  return (
    <section className="pt-32 pb-16 md:pt-40 md:pb-20 overflow-hidden">
      <div className="container-custom">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          <div className="space-y-6 max-w-2xl mx-auto lg:mx-0 text-center lg:text-left">
            <div className="inline-block animate-fade-in">
              <span className="px-3 py-1 rounded-full bg-medical/10 text-medical-dark text-sm font-medium">
                {t('classification.aiPowered')}
              </span>
            </div>

            <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold tracking-tight text-slate-900 dark:text-white animate-slide-up" style={{ animationDelay: '0.1s' }}>
              {t('classification.title')}
              <span className="text-medical dark:text-medical-light block md:inline"> Reimagined</span>
            </h1>

            <p className="text-lg md:text-xl text-slate-600 dark:text-slate-300 animate-slide-up" style={{ animationDelay: '0.2s' }}>
              {t('classification.subtitle')}
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start animate-slide-up" style={{ animationDelay: '0.3s' }}>
              <Link to="/#classification-tool" className="neuro-button-primary flex items-center justify-center gap-2">
                {t('classification.uploadScan')} <ChevronRight className="h-4 w-4" />
              </Link>
              <Link to="/about" className="neuro-button-outline">
                {t('navigation.about')}
              </Link>
            </div>

            <div className="pt-4 animate-slide-up" style={{ animationDelay: '0.4s' }}>
              <div className="flex flex-wrap gap-4 justify-center lg:justify-start">
                <FeatureTag icon={Brain} text={t('classification.neuralNetwork')} />
                <FeatureTag icon={Microscope} text={t('classification.accuracy')} />
                <FeatureTag icon={Dna} text={t('classification.geneticCorrelation')} />
              </div>
            </div>
          </div>

          <div className="relative hidden lg:block animate-fade-in" style={{ animationDelay: '0.5s' }}>
            <div className="absolute inset-0 bg-gradient-to-r from-medical/20 to-neuro-dark/20 rounded-3xl -rotate-6 scale-95 blur-xl animate-pulse opacity-70"></div>
            <div className="relative bg-white dark:bg-slate-800 rounded-2xl shadow-xl overflow-hidden border border-slate-200 dark:border-slate-700">
              <div className="h-8 bg-slate-100 dark:bg-slate-700 flex items-center px-4 border-b border-slate-200 dark:border-slate-600">
                <div className="flex space-x-2">
                  <div className="w-3 h-3 rounded-full bg-slate-300 dark:bg-slate-500"></div>
                  <div className="w-3 h-3 rounded-full bg-slate-300 dark:bg-slate-500"></div>
                  <div className="w-3 h-3 rounded-full bg-slate-300 dark:bg-slate-500"></div>
                </div>
              </div>
              <div className="relative aspect-square h-96 w-full bg-white dark:bg-slate-800 overflow-hidden">
                <div className="absolute inset-0 bg-gradient-to-br from-medical-light via-neuro-light to-white dark:from-medical-dark dark:via-neuro-dark dark:to-slate-900 animate-pulse opacity-60"></div>
                <div className="absolute inset-0 flex items-center justify-center">
                  <Brain className="w-32 h-32 text-medical/20 dark:text-medical/30" strokeWidth={1} />
                </div>
                <img
                  src="https://images.unsplash.com/photo-1559757175-7cb036bd4d31?q=80&w=1000&auto=format&fit=crop"
                  alt="Brain MRI scan visualization"
                  className="absolute inset-0 object-cover w-full h-full mix-blend-multiply dark:mix-blend-normal opacity-90"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

const FeatureTag = ({ icon: Icon, text }: { icon: any; text: string }) => {
  return (
    <div className="flex items-center gap-2 px-3 py-1.5 bg-slate-100 dark:bg-slate-800 rounded-full text-slate-800 dark:text-slate-200 text-sm">
      <Icon className="h-4 w-4 text-medical dark:text-medical-light" />
      <span>{text}</span>
    </div>
  );
};

export default Hero;
