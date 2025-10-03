import { Patient } from '@/data/mockPatients';
import { jsPDF } from 'jspdf';
import autoTable from 'jspdf-autotable';
import * as XLSX from 'xlsx';

// Export patient data to PDF
export const exportToPDF = (patients: Patient[]) => {
  try {
    const doc = new jsPDF();
    
    // Add title
    doc.setFontSize(18);
    doc.text('Patient List', 14, 22);
    doc.setFontSize(11);
    doc.text(`Generated on ${new Date().toLocaleDateString()}`, 14, 30);
    
    // Prepare data for table
    const tableColumn = ["ID", "Name", "Gender", "Date of Birth", "Contact", "Doctor"];
    const tableRows = patients.map(patient => [
      patient.id,
      `${patient.firstName} ${patient.lastName}`,
      patient.gender,
      new Date(patient.dateOfBirth).toLocaleDateString(),
      patient.contactNumber,
      patient.doctor
    ]);
    
    // Generate table
    autoTable(doc, {
      head: [tableColumn],
      body: tableRows,
      startY: 40,
      styles: {
        fontSize: 10,
        cellPadding: 3,
        lineColor: [0, 0, 0],
        lineWidth: 0.1,
      },
      headStyles: {
        fillColor: [66, 139, 202],
        textColor: [255, 255, 255],
        fontStyle: 'bold',
      },
      alternateRowStyles: {
        fillColor: [240, 240, 240],
      },
    });
    
    // Save the PDF
    doc.save('patient-list.pdf');
  } catch (error) {
    console.error('Error exporting to PDF:', error);
    alert('Failed to export to PDF. Please try again later.');
  }
};

// Export patient data to Excel
export const exportToExcel = (patients: Patient[]) => {
  try {
    // Prepare data for Excel
    const worksheet = XLSX.utils.json_to_sheet(
      patients.map(patient => ({
        ID: patient.id,
        'First Name': patient.firstName,
        'Last Name': patient.lastName,
        'Date of Birth': new Date(patient.dateOfBirth).toLocaleDateString(),
        Age: calculateAge(patient.dateOfBirth),
        Gender: patient.gender,
        'Contact Number': patient.contactNumber,
        Email: patient.email,
        'Blood Type': patient.bloodType,
        'Assigned Doctor': patient.doctor,
        'Last Scan': new Date(patient.lastScan).toLocaleDateString(),
        'Last Visit': new Date(patient.lastVisit).toLocaleDateString(),
        'Next Appointment': patient.nextAppointment ? new Date(patient.nextAppointment).toLocaleDateString() : 'None',
      }))
    );
    
    // Set column widths
    const columnWidths = [
      { wch: 5 },  // ID
      { wch: 15 }, // First Name
      { wch: 15 }, // Last Name
      { wch: 15 }, // Date of Birth
      { wch: 5 },  // Age
      { wch: 10 }, // Gender
      { wch: 20 }, // Contact Number
      { wch: 25 }, // Email
      { wch: 10 }, // Blood Type
      { wch: 20 }, // Assigned Doctor
      { wch: 15 }, // Last Scan
      { wch: 15 }, // Last Visit
      { wch: 15 }, // Next Appointment
    ];
    worksheet['!cols'] = columnWidths;
    
    // Create workbook
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, 'Patients');
    
    // Generate Excel file
    XLSX.writeFile(workbook, 'patient-list.xlsx');
  } catch (error) {
    console.error('Error exporting to Excel:', error);
    alert('Failed to export to Excel. Please try again later.');
  }
};

// Calculate age from date of birth
const calculateAge = (dateOfBirth: string): number => {
  const today = new Date();
  const birthDate = new Date(dateOfBirth);
  let age = today.getFullYear() - birthDate.getFullYear();
  const m = today.getMonth() - birthDate.getMonth();
  if (m < 0 || (m === 0 && today.getDate() < birthDate.getDate())) {
    age--;
  }
  return age;
};
