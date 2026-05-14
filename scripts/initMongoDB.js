import { insertSampleAnalyticsData } from '../services/analyticsService';

// Initialize MongoDB with sample data
async function initializeDatabase() {
  try {
    console.log('Initializing MongoDB with sample analytics data...');
    const result = await insertSampleAnalyticsData();
    console.log('MongoDB initialization completed successfully!');
    console.log(`Inserted ${result.insertedCount} records`);
    return result;
  } catch (error) {
    console.error('Failed to initialize MongoDB:', error);
    throw error;
  }
}

// Run initialization if this script is executed directly
if (typeof window === 'undefined' && typeof module !== 'undefined' && module.exports) {
  initializeDatabase()
    .then(() => {
      console.log('Database initialization complete');
      process.exit(0);
    })
    .catch((error) => {
      console.error('Database initialization failed:', error);
      process.exit(1);
    });
}

export { initializeDatabase };
