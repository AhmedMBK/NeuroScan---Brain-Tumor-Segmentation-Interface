
import Hero from '@/components/Hero';
import ClassificationTool from '@/components/ClassificationTool';
import Footer from '@/components/Footer';
import { useEffect } from 'react';

const Index = () => {
  // Smooth scroll for anchor links
  useEffect(() => {
    const handleAnchorClick = (e: MouseEvent) => {
      const target = e.target as HTMLElement;
      const closestAnchor = target.closest('a');

      if (closestAnchor && closestAnchor.hash && closestAnchor.hash.startsWith('#')) {
        e.preventDefault();
        const targetId = closestAnchor.hash.substring(1);
        const targetElement = document.getElementById(targetId);

        if (targetElement) {
          window.scrollTo({
            top: targetElement.offsetTop - 100,
            behavior: 'smooth'
          });

          // Update URL without scrolling
          window.history.pushState(null, '', closestAnchor.hash);
        }
      }
    };

    document.addEventListener('click', handleAnchorClick);
    return () => document.removeEventListener('click', handleAnchorClick);
  }, []);

  return (
    <>
      <Hero />
      <ClassificationTool />
      <Footer />
    </>
  );
};

export default Index;
