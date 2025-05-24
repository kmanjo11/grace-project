// Simple test script to check Mango V3 chart data
const axios = require('axios');

const MANGO_V3_BASE_URL = 'http://localhost:8000';
const marketName = 'SOL-PERP'; // Test with SOL perpetual market
const resolution = '1h';

async function testGetChartData() {
  try {
    console.log(`Attempting to fetch chart data from: ${MANGO_V3_BASE_URL}/api/markets/${marketName}/candles`);
    
    const response = await axios.get(
      `${MANGO_V3_BASE_URL}/api/markets/${marketName}/candles`,
      {
        params: {
          resolution: resolution
        }
      }
    );
    
    console.log('Response status:', response.status);
    console.log('Response headers:', response.headers);
    
    // Check if we got valid data
    if (Array.isArray(response.data) && response.data.length > 0) {
      console.log(`Successfully retrieved ${response.data.length} candles`);
      console.log('First 3 candles:', response.data.slice(0, 3));
      
      // Validate data structure matches what PriceChart expects
      const hasValidStructure = response.data.every(item => 
        item && 
        typeof item.time === 'number' &&
        'open' in item &&
        'high' in item &&
        'low' in item &&
        'close' in item
      );
      
      console.log('Data has valid structure:', hasValidStructure);
    } else {
      console.error('Invalid response format:', response.data);
    }
    
  } catch (error) {
    console.error('Error fetching chart data:');
    if (error.response) {
      // The request was made and the server responded with a status code
      // that falls out of the range of 2xx
      console.error('Response status:', error.response.status);
      console.error('Response data:', error.response.data);
      console.error('Response headers:', error.response.headers);
    } else if (error.request) {
      // The request was made but no response was received
      console.error('No response received');
    } else {
      // Something happened in setting up the request that triggered an Error
      console.error('Error message:', error.message);
    }
  }
}

// Also test the market search functionality
async function testSearchMarkets() {
  try {
    console.log(`Attempting to search markets from: ${MANGO_V3_BASE_URL}/api/markets`);
    
    const response = await axios.get(
      `${MANGO_V3_BASE_URL}/api/markets`,
      {
        params: {
          q: 'SOL'
        }
      }
    );
    
    console.log('Response status:', response.status);
    
    // Check if we got valid data
    if (Array.isArray(response.data) && response.data.length > 0) {
      console.log(`Successfully found ${response.data.length} markets`);
      console.log('Markets:', response.data);
    } else {
      console.error('Invalid response format or no markets found:', response.data);
    }
    
  } catch (error) {
    console.error('Error searching markets:');
    if (error.response) {
      console.error('Response status:', error.response.status);
      console.error('Response data:', error.response.data);
    } else if (error.request) {
      console.error('No response received');
    } else {
      console.error('Error message:', error.message);
    }
  }
}

// Run both tests
(async () => {
  console.log('======= TESTING MANGO V3 CHART DATA =======');
  await testGetChartData();
  
  console.log('\n======= TESTING MANGO V3 MARKET SEARCH =======');
  await testSearchMarkets();
})();
