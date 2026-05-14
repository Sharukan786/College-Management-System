// Real MongoDB analytics service - fetches from backend API

import { API_BASE } from '../api/apiBase';

// Fetch real analytics data from MongoDB with optional filters
export async function getRealAnalyticsData(year = null, semester = null, department = null) {
  try {
    // Build query string with filters
    const params = new URLSearchParams();
    if (year) params.append('year', year);
    if (semester) params.append('semester', semester);
    if (department) params.append('department', department);
    
    const queryString = params.toString();
    const url = `${API_BASE}/analytics/dashboard${queryString ? '?' + queryString : ''}`;
    
    const response = await fetch(url);
    
    if (!response.ok) {
      throw new Error('Failed to fetch analytics data');
    }
    
    const result = await response.json();
    
    if (result.success && result.data) {
      return result.data;
    }
    
    throw new Error('Invalid response format');
  } catch (error) {
    console.error('Error fetching real analytics:', error);
    return null;
  }
}

// Legacy function - now fetches real data with filters
export async function getAnalyticsData(year, semester, department = null) {
  return getRealAnalyticsData(year, semester, department);
}

// No longer needed - data comes from real MongoDB
export async function insertSampleAnalyticsData() {
  console.log('Using real MongoDB data - no sample initialization needed');
  return { message: 'Using real MongoDB data' };
}

// Get all analytics data with filters
export async function getAllAnalyticsData(year = null, semester = null, department = null) {
  return getRealAnalyticsData(year, semester, department);
}
