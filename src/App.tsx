
import { Suspense, lazy, useEffect } from 'react';
import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, Outlet, Navigate } from "react-router-dom";
import { AuthProvider } from "@/contexts/AuthContext";
import { ThemeProvider } from "@/contexts/ThemeContext";
import Navbar from "@/components/Navbar";
import ProtectedRoute from "@/components/ProtectedRoute";
import DoctorProfileGuard from "@/components/auth/DoctorProfileGuard";


// Lazy load pages for better performance
const Index = lazy(() => import("./pages/Index"));
const About = lazy(() => import("./pages/About"));
const Login = lazy(() => import("./pages/Login"));

const Dashboard = lazy(() => import("./pages/Dashboard"));
const Patients = lazy(() => import("./pages/Patients"));
const PatientCreate = lazy(() => import("./pages/PatientCreate"));
const PatientDetail = lazy(() => import("./pages/PatientDetail"));
const PatientEdit = lazy(() => import("./pages/PatientEdit"));
const PatientExamHistory = lazy(() => import("./pages/PatientExamHistory"));
const PatientTreatmentTracking = lazy(() => import("./pages/PatientTreatmentTracking"));
const ImageUpload = lazy(() => import("./pages/ImageUpload"));
const Users = lazy(() => import("./pages/Users"));
const Doctors = lazy(() => import("./pages/Doctors"));
const Reports = lazy(() => import("./pages/Reports"));
const ReportView = lazy(() => import("./pages/ReportView"));
const Settings = lazy(() => import("./pages/Settings"));
const Unauthorized = lazy(() => import("./pages/Unauthorized"));
const NotFound = lazy(() => import("./pages/NotFound"));

// ✅ AJOUTÉ : Pages spécifiques pour les rôles
const SecretaryManagement = lazy(() => import("./pages/SecretaryManagement"));
const SecretaryAppointments = lazy(() => import("./pages/SecretaryAppointments"));

const queryClient = new QueryClient();

// Layout component with Navbar
const Layout = () => {
  return (
    <div className="min-h-screen flex flex-col bg-white dark:bg-slate-900">
      <Navbar />
      <main className="flex-grow pt-20">
        <Outlet />
      </main>
    </div>
  );
};

const App = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <ThemeProvider>
          <TooltipProvider>
            <Toaster />
            <Sonner />
            <BrowserRouter>
              <Suspense fallback={
                <div className="flex items-center justify-center min-h-screen">
                  <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-medical"></div>
                </div>
              }>
                <Routes>
                  {/* Redirection par défaut vers login */}
                  <Route path="/" element={<Navigate to="/login" replace />} />

                  {/* Routes publiques (sans authentification) */}
                  <Route path="/login" element={<Login />} />
                  <Route path="/unauthorized" element={<Unauthorized />} />
                  <Route path="/about" element={<About />} />

                  {/* Routes protégées avec Navbar */}
                  <Route element={<Layout />}>
                    <Route path="/dashboard" element={
                      <ProtectedRoute>
                        <DoctorProfileGuard>
                          <Dashboard />
                        </DoctorProfileGuard>
                      </ProtectedRoute>
                    } />
                    <Route path="/patients" element={
                      <ProtectedRoute>
                        <Patients />
                      </ProtectedRoute>
                    } />
                    <Route path="/patients/new" element={
                      <ProtectedRoute>
                        <PatientCreate />
                      </ProtectedRoute>
                    } />
                    <Route path="/patients/:id" element={
                      <ProtectedRoute>
                        <PatientDetail />
                      </ProtectedRoute>
                    } />
                    <Route path="/patients/:patientId/upload" element={
                      <ProtectedRoute>
                        <ImageUpload />
                      </ProtectedRoute>
                    } />
                    <Route path="/patients/:id/edit" element={
                      <ProtectedRoute>
                        <PatientEdit />
                      </ProtectedRoute>
                    } />
                    <Route path="/patients/:id/scans" element={
                      <ProtectedRoute>
                        <PatientDetail />
                      </ProtectedRoute>
                    } />
                    <Route path="/patients/:id/exam-history" element={
                      <ProtectedRoute>
                        <PatientExamHistory />
                      </ProtectedRoute>
                    } />
                    <Route path="/patients/:id/treatment-tracking" element={
                      <ProtectedRoute>
                        <PatientTreatmentTracking />
                      </ProtectedRoute>
                    } />
                    <Route path="/settings" element={
                      <ProtectedRoute>
                        <Settings />
                      </ProtectedRoute>
                    } />
                    <Route path="/users" element={
                      <ProtectedRoute allowedRoles={['ADMIN']}>
                        <Users />
                      </ProtectedRoute>
                    } />
                    <Route path="/doctors" element={
                      <ProtectedRoute allowedRoles={['ADMIN']}>
                        <Doctors />
                      </ProtectedRoute>
                    } />
                    <Route path="/reports" element={
                      <ProtectedRoute allowedRoles={['ADMIN', 'DOCTOR']}>
                        <Reports />
                      </ProtectedRoute>
                    } />
                    <Route path="/reports/:reportId" element={
                      <ProtectedRoute allowedRoles={['ADMIN', 'DOCTOR']}>
                        <ReportView />
                      </ProtectedRoute>
                    } />

                    {/* ✅ AJOUTÉ : Routes pour médecins */}
                    <Route path="/secretaries" element={
                      <ProtectedRoute allowedRoles={['DOCTOR']}>
                        <SecretaryManagement />
                      </ProtectedRoute>
                    } />

                    {/* ✅ AJOUTÉ : Routes pour secrétaires */}
                    <Route path="/secretary/appointments" element={
                      <ProtectedRoute allowedRoles={['SECRETARY']}>
                        <SecretaryAppointments />
                      </ProtectedRoute>
                    } />
                  </Route>

                  {/* Catch-all route */}
                  <Route path="*" element={<NotFound />} />
                </Routes>
              </Suspense>
            </BrowserRouter>
          </TooltipProvider>
        </ThemeProvider>
      </AuthProvider>
    </QueryClientProvider>
  );
};

export default App;
