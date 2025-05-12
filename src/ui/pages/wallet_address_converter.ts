import { Buffer } from 'buffer';
import bs58 from 'bs58';

// Cool crypto-inspired prefixes
const COOL_PREFIXES = [
  '🚀', '💎', '🌟', '⚡', '🔥', '🤖', 
  'MOON', 'DEGEN', 'CHAD', 'BASED', 'ALPHA'
];

/**
 * Converts various wallet addresses to ultra-cool crypto bro formats
 */
export class WalletAddressConverter {
  /**
   * Convert binary/hex wallet address to base58 Solana-style address
   * @param address Raw wallet address (binary, hex, or other format)
   * @returns Formatted Solana-style wallet address
   */
  static convertToSolanaAddress(address: string | Buffer): string {
    try {
      // If it's already a valid-looking Solana address, return as-is
      if (typeof address === 'string' && /^[1-9A-HJ-NP-Za-km-z]{32,44}$/.test(address)) {
        return address;
      }

      // Convert hex string to buffer
      let buffer: Buffer;
      if (typeof address === 'string') {
        // Remove '0x' prefix if present
        const cleanAddress = address.startsWith('0x') ? address.slice(2) : address;
        
        // Handle hex string
        if (/^[0-9a-fA-F]+$/.test(cleanAddress)) {
          buffer = Buffer.from(cleanAddress, 'hex');
        } 
        // Handle escaped hex string
        else if (address.includes('\\x')) {
          // Remove '\x' and spaces, then convert
          const cleanHex = address.replace(/\\x/g, '').replace(/\s/g, '');
          buffer = Buffer.from(cleanHex, 'hex');
        } 
        // Assume it's a binary string
        else {
          buffer = Buffer.from(address, 'binary');
        }
      } 
      // If already a buffer, use as-is
      else {
        buffer = address;
      }

      // Truncate to standard Solana public key length (32 bytes)
      const truncatedBuffer = buffer.slice(0, 32);
      
      // Create a new buffer with proper length (32 bytes)
      const standardBuffer = Buffer.alloc(32);
      truncatedBuffer.copy(standardBuffer);

      // Convert to base58
      return bs58.encode(standardBuffer);
    } catch (error) {
      console.error('Failed to convert wallet address:', error);
      return 'Invalid Address';
    }
  }

  /**
   * Generate a human-readable wallet identifier
   * @param address Raw wallet address
   * @returns Shortened, readable wallet identifier
   */
  static generateReadableIdentifier(address: string | Buffer): string {
    const solanaAddress = this.convertToSolanaAddress(address);
    
    // Return first 4 and last 4 characters
    return `${solanaAddress.slice(0, 4)}...${solanaAddress.slice(-4)}`;
  }

  /**
   * Validate and format wallet address
   * @param address Raw wallet address
   * @returns Validated and formatted wallet information
   */
  static formatWalletAddress(address: string | Buffer): {
    fullAddress: string;
    shortAddress: string;
    coolAddress: string;
    isValid: boolean;
  } {
    try {
      const fullAddress = this.convertToSolanaAddress(address);
      return {
        fullAddress,
        shortAddress: this.generateReadableIdentifier(fullAddress),
        coolAddress: this.generateCryptoBroAddress(fullAddress),
        isValid: true
      };
    } catch (error) {
      return {
        fullAddress: 'Invalid Address',
        shortAddress: 'Invalid',
        coolAddress: 'REKT 💥',
        isValid: false
      };
    }
  }

  /**
   * Generate a hyper-cool crypto bro wallet address
   * @param address Base58 wallet address
   * @returns Ultra-cool wallet identifier
   */
  static generateCryptoBroAddress(address: string): string {
    // Get a random cool prefix
    const prefix = COOL_PREFIXES[Math.floor(Math.random() * COOL_PREFIXES.length)];
    
    // Take first 4 and last 4 chars of address
    const addressCore = `${address.slice(0, 4)}...${address.slice(-4)}`;
    
    // Combine with some crypto swag
    return `${prefix} ${addressCore} 💎`;
  }
}

// Example usage
export function convertWalletAddress(rawAddress: string): string {
  return WalletAddressConverter.convertToSolanaAddress(rawAddress);
}

// Bonus: Crypto Bro Address Generator
export function getCryptoBroWalletName(address?: string): string {
  if (!address) {
    // Random cool wallet name for the true degens
    const degenNames = [
      'MOON WALLET 🚀', 
      'CHAD CRYPTO 💎', 
      'DEGEN VAULT 🔥', 
      'ALPHA STASH ⚡'
    ];
    return degenNames[Math.floor(Math.random() * degenNames.length)];
  }
  
  return WalletAddressConverter.generateCryptoBroAddress(address);
}
