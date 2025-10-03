
import Footer from '@/components/Footer';
import { useTranslation } from 'react-i18next';
import { Brain, BarChart3, Microscope, Heart, FileText, Dna, Activity, ChevronRight } from 'lucide-react';
import { Link } from 'react-router-dom';

const About = () => {
  const { t } = useTranslation();
  return (
    <>
        {/* Hero Section */}
        <section className="pt-32 pb-16 bg-gradient-to-b from-slate-50 dark:from-slate-800 to-white dark:to-slate-900">
          <div className="container-custom">
            <div className="max-w-3xl mx-auto text-center">
              <h1 className="text-4xl md:text-5xl font-bold text-slate-900 dark:text-white mb-6 animate-slide-up">
                {t('about.title')}
              </h1>
              <p className="text-xl text-slate-600 dark:text-slate-300 mb-8 animate-slide-up" style={{ animationDelay: '0.1s' }}>
                {t('about.subtitle')}
              </p>
              <div className="animate-slide-up" style={{ animationDelay: '0.2s' }}>
                <Link to="/#classification-tool" className="neuro-button-primary inline-flex items-center gap-2">
                  {t('about.tryOurTool')} <ChevronRight className="h-4 w-4" />
                </Link>
              </div>
            </div>
          </div>
        </section>

        {/* Mission Section */}
        <section className="py-20">
          <div className="container-custom">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
              <div>
                <span className="px-3 py-1 rounded-full bg-medical/10 dark:bg-medical/20 text-medical-dark dark:text-medical-light text-sm font-medium">
                  {t('about.mission')}
                </span>
                <h2 className="text-3xl md:text-4xl font-bold text-slate-900 dark:text-white mt-4 mb-6">
                  {t('about.missionTitle')}
                </h2>
                <p className="text-lg text-slate-600 dark:text-slate-300 mb-6">
                  {t('about.missionText1')}
                </p>
                <p className="text-lg text-slate-600 dark:text-slate-300 mb-6">
                  {t('about.missionText2')}
                </p>
                <div className="flex flex-wrap gap-4">
                  <div className="flex items-center gap-2 px-4 py-2 bg-slate-100 dark:bg-slate-800 rounded-lg">
                    <Heart className="h-5 w-5 text-medical dark:text-medical-light" />
                    <span className="text-slate-700 dark:text-slate-200 font-medium">{t('about.improvingPatientCare')}</span>
                  </div>
                  <div className="flex items-center gap-2 px-4 py-2 bg-slate-100 dark:bg-slate-800 rounded-lg">
                    <Activity className="h-5 w-5 text-medical dark:text-medical-light" />
                    <span className="text-slate-700 dark:text-slate-200 font-medium">{t('about.reducingDiagnosisTime')}</span>
                  </div>
                </div>
              </div>

              <div className="relative">
                <div className="absolute inset-0 bg-gradient-to-r from-medical/10 to-neuro-dark/10 dark:from-medical/20 dark:to-neuro-dark/20 rounded-3xl -rotate-3 scale-95 blur-xl"></div>
                <img
                  src="https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?ixlib=rb-4.0.3&auto=format&fit=crop&w=2070&q=80"
                  alt="Advanced medical technology"
                  className="relative rounded-xl shadow-lg object-cover aspect-video border border-transparent dark:border-slate-700"
                />
              </div>
            </div>
          </div>
        </section>

        {/* Technology Section */}
        <section className="py-20 bg-slate-50 dark:bg-slate-800">
          <div className="container-custom">
            <div className="text-center max-w-3xl mx-auto mb-16">
              <span className="px-3 py-1 rounded-full bg-medical/10 dark:bg-medical/20 text-medical-dark dark:text-medical-light text-sm font-medium">
                {t('about.technology')}
              </span>
              <h2 className="text-3xl md:text-4xl font-bold text-slate-900 dark:text-white mt-4 mb-6">
                {t('about.technologyTitle')}
              </h2>
              <p className="text-lg text-slate-600 dark:text-slate-300">
                {t('about.technologyText')}
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              <TechCard
                icon={Brain}
                title={t('about.deepLearning')}
                description={t('about.deepLearningText')}
              />
              <TechCard
                icon={BarChart3}
                title={t('about.statisticalAnalysis')}
                description={t('about.statisticalAnalysisText')}
              />
              <TechCard
                icon={Dna}
                title={t('about.geneticCorrelation')}
                description={t('about.geneticCorrelationText')}
              />
            </div>
          </div>
        </section>

        {/* Team Section */}
        <section className="py-20">
          <div className="container-custom">
            <div className="text-center max-w-3xl mx-auto mb-16">
              <span className="px-3 py-1 rounded-full bg-medical/10 dark:bg-medical/20 text-medical-dark dark:text-medical-light text-sm font-medium">
                {t('about.expertise')}
              </span>
              <h2 className="text-3xl md:text-4xl font-bold text-slate-900 dark:text-white mt-4 mb-6">
                {t('about.expertiseTitle')}
              </h2>
              <p className="text-lg text-slate-600 dark:text-slate-300">
                {t('about.expertiseText')}
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
              <TeamMember
                name="Dr. Emma Chen"
                role="Chief Medical Officer"
                specialty="Neuroradiology"
              />
              <TeamMember
                name="Dr. Michael Rodriguez"
                role="Research Director"
                specialty="Oncology"
              />
              <TeamMember
                name="Sarah Johnson, PhD"
                role="AI Lead"
                specialty="Computer Vision"
              />
              <TeamMember
                name="James Wilson, MSc"
                role="Data Scientist"
                specialty="Medical Imaging"
              />
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="py-20 bg-gradient-to-br from-medical-light via-neuro-light to-white dark:from-medical-dark dark:via-neuro-dark dark:to-slate-900">
          <div className="container-custom">
            <div className="max-w-3xl mx-auto text-center">
              <span className="px-3 py-1 rounded-full bg-medical/20 dark:bg-medical/30 text-medical-dark dark:text-medical-light text-sm font-medium">
                {t('about.getStarted')}
              </span>
              <h2 className="text-3xl md:text-4xl font-bold text-slate-900 dark:text-white mt-4 mb-6">
                {t('about.getStartedTitle')}
              </h2>
              <p className="text-xl text-slate-700 dark:text-slate-300 mb-8">
                {t('about.getStartedText')}
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Link to="/#classification-tool" className="neuro-button-primary">
                  {t('about.startClassification')}
                </Link>
                <a href="#" className="neuro-button-outline">
                  {t('about.requestApiAccess')}
                </a>
              </div>
            </div>
          </div>
        </section>
      <Footer />
    </>
  );
};

const TechCard = ({ icon: Icon, title, description }: { icon: any, title: string, description: string }) => {
  return (
    <div className="bg-white dark:bg-slate-900 rounded-xl p-6 shadow-sm border border-slate-200 dark:border-slate-700 hover:shadow-md transition-shadow h-full">
      <div className="w-12 h-12 rounded-lg bg-medical/10 dark:bg-medical/20 flex items-center justify-center mb-4">
        <Icon className="h-6 w-6 text-medical dark:text-medical-light" />
      </div>
      <h3 className="text-xl font-semibold text-slate-800 dark:text-white mb-3">{title}</h3>
      <p className="text-slate-600 dark:text-slate-300">{description}</p>
    </div>
  );
};

const TeamMember = ({ name, role, specialty }: { name: string, role: string, specialty: string }) => {
  return (
    <div className="bg-white dark:bg-slate-900 rounded-xl overflow-hidden shadow-sm border border-slate-200 dark:border-slate-700 hover:shadow-md transition-shadow">
      <div className="aspect-square bg-slate-100 dark:bg-slate-800 flex items-center justify-center">
        <Microscope className="h-16 w-16 text-slate-300 dark:text-slate-600" strokeWidth={1} />
      </div>
      <div className="p-5">
        <h3 className="text-lg font-semibold text-slate-800 dark:text-white">{name}</h3>
        <p className="text-medical dark:text-medical-light font-medium text-sm">{role}</p>
        <p className="text-slate-500 dark:text-slate-400 text-sm mt-1">{specialty}</p>
      </div>
    </div>
  );
};

export default About;
