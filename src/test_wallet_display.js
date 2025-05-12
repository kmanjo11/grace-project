/**
 * Test wallet address display functionality
 * This script tests the cleanWalletAddress function with various wallet address formats
 * to ensure it properly cleans and displays them.
 */

// Import the cleanWalletAddress function from app.js
// In a real test environment, we'd use proper imports
// For this test, we'll just copy the function here

/**
 * Clean wallet address by removing unwanted characters
 * @param {string} address - The wallet address to clean
 * @returns {string} Cleaned wallet address
 */
function cleanWalletAddress(address) {
    if (!address) return '';

    // First, check if it's already a clean address (only alphanumeric and possibly some special chars)
    const cleanPattern = /^[a-zA-Z0-9]{30,50}$/;
    if (cleanPattern.test(address)) {
        return address; // Already clean
    }

    // Check if it's a byte representation (starts with b' and contains \\x)
    if (address.startsWith("b'") && address.includes('\\x')) {
        // This is a Python-style byte representation
        // Extract the hex values
        let hexString = '';
        const hexMatches = address.match(/\\x([0-9a-fA-F]{2})/g);

        if (hexMatches) {
            // Convert each \x00 to its hex value
            hexMatches.forEach(match => {
                hexString += match.substring(2); // Remove the \x part
            });

            // Also get any regular characters (non-escaped)
            const parts = address.split('\\x');
            for (let i = 0; i < parts.length; i++) {
                if (i === 0) {
                    // First part might have b'
                    const firstPart = parts[i].replace("b'", "");
                    if (firstPart) {
                        // Convert each character to its hex representation
                        for (let j = 0; j < firstPart.length; j++) {
                            hexString += firstPart.charCodeAt(j).toString(16).padStart(2, '0');
                        }
                    }
                } else {
                    // For other parts, the first 2 chars are the hex value we already processed
                    // But there might be more characters after
                    if (parts[i].length > 2) {
                        const remainingChars = parts[i].substring(2);
                        // Handle the closing quote if present
                        const cleanPart = remainingChars.replace(/['"]$/, '');
                        for (let j = 0; j < cleanPart.length; j++) {
                            hexString += cleanPart.charCodeAt(j).toString(16).padStart(2, '0');
                        }
                    }
                }
            }

            return hexString;
        }
    }

    // For Solana addresses that contain escape characters
    if (address.includes('\\\\') || address.includes('"') || address.includes('\'')) {
        // Remove escape characters and quotes
        let cleaned = address.replace(/\\\\|\"|'/g, '');

        // Further clean to keep only alphanumeric characters
        cleaned = cleaned.replace(/[^a-zA-Z0-9]/g, '');

        return cleaned;
    }

    // For other addresses, just keep alphanumeric characters
    return address.replace(/[^a-zA-Z0-9]/g, '');
}

// Test cases - these represent different formats of wallet addresses we might encounter
const testCases = [
    // Python byte representation (common in our backend)
    "b'\\x86\\xd2\\xa1\\xc7\\xb8\\x2f\\xca\\xc1\\xae\\xf4\\x86\\x1b\\xbe\\xa1\\xd7\\x91\\x81: \\xf1=\\xd3\\x7f\\x0f\\xe6\\xc9\\xb9\\x06Q'",
    
    // Address with escape characters
    "b'\\v0b\\v88\\v803\\vb\\v5\\v2f5\\v0\\v86\\v1d\\vc1\\v0eq\\vd0f\\vf0\\v9a3on1\\veb\\v2\\vc1\\v1f\\vcdM\\vdd'",
    
    // Address with quotes and other characters
    "'G92hAoG'",
    
    // Clean address (should remain unchanged)
    "5XZzeS5G92hAoG123456789012345678901234567890",
    
    // Address with other non-alphanumeric characters
    "5XZz-eS5-G92h-AoG-1234-5678-9012-3456-7890-1234-5678-90",
    
    // Empty or null address
    "",
    null,
    
    // Real example from the screenshot
    "b'Gv1a\\x97\\x82\\xac\\xae\\xf4\\x86\\1b\\be\\a1\\d7\\x91\\x81: \\xf1=\\xd3K\\x7f\\x0f\\xe6\\c\\x9b9\\x06Q'"
];

// Run the tests
console.log("WALLET ADDRESS CLEANING TEST RESULTS:");
console.log("=====================================");

testCases.forEach((address, index) => {
    const cleaned = cleanWalletAddress(address);
    console.log(`Test Case ${index + 1}:`);
    console.log(`  Original: ${address}`);
    console.log(`  Cleaned:  ${cleaned}`);
    console.log("-------------------------------------");
});

// Test the updateInternalWalletUI function with a mock wallet data object
console.log("\nTESTING WALLET UI UPDATE:");
console.log("=====================================");

// Mock wallet data
const mockWalletData = {
    address: "b'\\x86\\xd2\\xa1\\xc7\\xb8\\x2f\\xca\\xc1\\xae\\xf4\\x86\\x1b\\xbe\\xa1\\xd7\\x91\\x81: \\xf1=\\xd3\\x7f\\x0f\\xe6\\xc9\\xb9\\x06Q'",
    balances: [
        { token: 'SOL', amount: 1.5 },
        { token: 'USDC', amount: 100.0 }
    ]
};

// Mock updateInternalWalletUI function
function testUpdateInternalWalletUI(walletData) {
    if (!walletData) {
        console.log("No wallet data provided");
        return;
    }
    
    const rawAddress = walletData.address || 'demo-wallet-address';
    
    // Clean the address
    const cleanAddress = cleanWalletAddress(rawAddress);
    
    console.log(`Raw wallet address: ${rawAddress}`);
    console.log(`Cleaned wallet address: ${cleanAddress}`);
    
    // This is what would be displayed in the UI
    console.log(`UI would display: ${cleanAddress}`);
}

// Run the UI update test
testUpdateInternalWalletUI(mockWalletData);
