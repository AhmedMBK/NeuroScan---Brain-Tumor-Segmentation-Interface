
import { ClassificationResult } from '@/components/ResultView';

// Mock classification result data
const mockResults: ClassificationResult[] = [
  {
    tumorType: 'Glioblastoma (Grade IV)',
    confidence: 96.8,
    description: 'Glioblastoma is an aggressive type of cancer that can occur in the brain or spinal cord. This scan shows characteristics consistent with a high-grade glioblastoma with typical radiographic features.',
    recommendations: [
      'Urgent neurosurgical consultation for potential resection',
      'Advanced MRI imaging with contrast to assess vascularity',
      'Consider molecular testing to guide treatment options',
      'Evaluation for clinical trial eligibility'
    ],
    imageUrl: ''
  },
  {
    tumorType: 'Meningioma (Grade I)',
    confidence: 92.5,
    description: 'Meningiomas are typically benign tumors that arise from the meninges — the membranes that surround the brain and spinal cord. This scan reveals a well-defined, extra-axial mass consistent with a meningioma.',
    recommendations: [
      'Neurosurgical evaluation for potential resection',
      'Consider watchful waiting approach with serial imaging',
      'Radiation therapy may be an option if surgery is contraindicated',
      'Follow-up MRI in 3-6 months to assess growth rate'
    ],
    imageUrl: ''
  },
  {
    tumorType: 'Pituitary Adenoma',
    confidence: 88.3,
    description: 'Pituitary adenomas are benign tumors that arise from cells in the pituitary gland. This scan shows a sellar mass consistent with a pituitary adenoma with possible suprasellar extension.',
    recommendations: [
      'Endocrinological evaluation for hormonal imbalances',
      'Visual field testing to check for compression of optic chiasm',
      'Consider transsphenoidal surgical approach if symptomatic',
      'MRI with thin cuts through sella turcica for better visualization'
    ],
    imageUrl: ''
  },
  {
    tumorType: 'Astrocytoma (Grade II)',
    confidence: 79.6,
    description: 'Astrocytomas are tumors that arise from astrocytes — star-shaped cells that make up the supportive tissue of the brain. This scan indicates features of a diffuse, low-grade astrocytoma with minimal enhancement.',
    recommendations: [
      'Consider surgical biopsy for molecular characterization',
      'MR spectroscopy to assess metabolic activity',
      'Discuss observation versus early intervention strategies',
      'Neuropsychological testing to establish cognitive baseline'
    ],
    imageUrl: ''
  }
];

/**
 * Mock function to simulate image classification
 * In a real application, this would call an API or ML model
 */
export const classifyImage = async (imageUrl: string): Promise<ClassificationResult> => {
  // Simulate API call delay
  await new Promise(resolve => setTimeout(resolve, 2500));
  
  // Randomly select a classification result and add the image URL
  const randomIndex = Math.floor(Math.random() * mockResults.length);
  return {
    ...mockResults[randomIndex],
    imageUrl
  };
};
