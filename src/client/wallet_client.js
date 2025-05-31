/**
 * Client-side wallet management for Grace Project
 * 
 * This module provides client-side functionality for non-custodial wallets:
 * - Key generation
 * - Secure storage of private keys
 * - Transaction signing
 * - Integration with server-side wallet system
 */

import { Keypair } from '@solana/web3.js';
import { encode as base58Encode, decode as base58Decode } from 'bs58';
import CryptoJS from 'crypto-js';

class NonCustodialWalletClient {
  constructor(apiClient, storagePrefix = 'grace_wallet_') {
    this.apiClient = apiClient;
    this.storagePrefix = storagePrefix;
    this.currentWallet = null;
  }

  /**
   * Generate a new wallet keypair
   * @returns {Object} Generated keypair
   */
  generateWallet() {
    const keypair = Keypair.generate();
    this.currentWallet = {
      publicKey: keypair.publicKey.toString(),
      secretKey: Array.from(keypair.secretKey)
    };
    return this.currentWallet;
  }

  /**
   * Encrypt private key with user password
   * @param {Array|Uint8Array} secretKey - Wallet secret key
   * @param {string} password - User password for encryption
   * @returns {string} Encrypted private key
   */
  encryptPrivateKey(secretKey, password) {
    const secretKeyString = JSON.stringify(Array.from(secretKey));
    return CryptoJS.AES.encrypt(secretKeyString, password).toString();
  }

  /**
   * Decrypt private key with user password
   * @param {string} encryptedKey - Encrypted private key
   * @param {string} password - User password for decryption
   * @returns {Uint8Array} Decrypted private key
   */
  decryptPrivateKey(encryptedKey, password) {
    try {
      const decrypted = CryptoJS.AES.decrypt(encryptedKey, password).toString(CryptoJS.enc.Utf8);
      return new Uint8Array(JSON.parse(decrypted));
    } catch (e) {
      console.error('Failed to decrypt private key:', e);
      throw new Error('Invalid password or corrupted key');
    }
  }

  /**
   * Store wallet securely in browser storage
   * @param {Object} wallet - Wallet object with publicKey and secretKey
   * @param {string} password - User password for encryption
   * @param {string} userId - User ID
   * @returns {boolean} Success status
   */
  storeWallet(wallet, password, userId) {
    try {
      const encryptedKey = this.encryptPrivateKey(wallet.secretKey, password);
      
      // Store encrypted private key
      localStorage.setItem(
        `${this.storagePrefix}${userId}_private_key`, 
        encryptedKey
      );
      
      // Store public key (unencrypted)
      localStorage.setItem(
        `${this.storagePrefix}${userId}_public_key`,
        wallet.publicKey
      );
      
      return true;
    } catch (e) {
      console.error('Failed to store wallet:', e);
      return false;
    }
  }

  /**
   * Load wallet from browser storage
   * @param {string} userId - User ID
   * @param {string} password - User password for decryption
   * @returns {Object|null} Loaded wallet or null if not found
   */
  loadWallet(userId, password) {
    try {
      const encryptedKey = localStorage.getItem(`${this.storagePrefix}${userId}_private_key`);
      const publicKey = localStorage.getItem(`${this.storagePrefix}${userId}_public_key`);
      
      if (!encryptedKey || !publicKey) {
        return null;
      }
      
      const secretKey = this.decryptPrivateKey(encryptedKey, password);
      
      this.currentWallet = {
        publicKey,
        secretKey
      };
      
      return this.currentWallet;
    } catch (e) {
      console.error('Failed to load wallet:', e);
      return null;
    }
  }

  /**
   * Register wallet with server
   * @param {string} userId - User ID
   * @returns {Promise} Server response
   */
  async registerWalletWithServer(userId) {
    if (!this.currentWallet) {
      throw new Error('No wallet available to register');
    }
    
    try {
      const response = await this.apiClient.post('/api/wallet/register-public-key', {
        userId,
        publicKey: this.currentWallet.publicKey
      });
      
      return response.data;
    } catch (e) {
      console.error('Failed to register wallet with server:', e);
      throw e;
    }
  }

  /**
   * Sign a transaction
   * @param {Transaction} transaction - Transaction to sign
   * @param {string} userId - User ID
   * @param {string} password - User password for decryption
   * @returns {Transaction} Signed transaction
   */
  signTransaction(transaction, userId, password) {
    // Load wallet if not already loaded
    if (!this.currentWallet) {
      this.loadWallet(userId, password);
    }
    
    if (!this.currentWallet) {
      throw new Error('No wallet available for signing');
    }
    
    // Create keypair from stored keys
    const keypair = Keypair.fromSecretKey(
      new Uint8Array(this.currentWallet.secretKey)
    );
    
    // Sign transaction
    transaction.sign(keypair);
    return transaction;
  }

  /**
   * Create and initialize a new wallet
   * @param {string} userId - User ID
   * @param {string} password - User password for encryption
   * @returns {Promise} Initialization result
   */
  async initializeNewWallet(userId, password) {
    try {
      // Generate new wallet
      this.generateWallet();
      
      // Store wallet locally
      const storeResult = this.storeWallet(this.currentWallet, password, userId);
      if (!storeResult) {
        throw new Error('Failed to store wallet locally');
      }
      
      // Register with server
      const registerResult = await this.registerWalletWithServer(userId);
      
      return {
        success: true,
        publicKey: this.currentWallet.publicKey,
        serverResponse: registerResult
      };
    } catch (e) {
      console.error('Failed to initialize wallet:', e);
      return {
        success: false,
        error: e.message
      };
    }
  }

  /**
   * Check if user has a stored wallet
   * @param {string} userId - User ID
   * @returns {boolean} Whether wallet exists
   */
  hasStoredWallet(userId) {
    const publicKey = localStorage.getItem(`${this.storagePrefix}${userId}_public_key`);
    const privateKey = localStorage.getItem(`${this.storagePrefix}${userId}_private_key`);
    return !!(publicKey && privateKey);
  }

  /**
   * Export wallet as seed phrase (mnemonic)
   * @param {string} userId - User ID
   * @param {string} password - User password for decryption
   * @returns {string} Seed phrase
   */
  exportWalletAsSeed(userId, password) {
    // This is a simplified implementation
    // In a real implementation, you would use BIP39 to generate a mnemonic
    // from the private key
    
    if (!this.currentWallet) {
      this.loadWallet(userId, password);
    }
    
    if (!this.currentWallet) {
      throw new Error('No wallet available for export');
    }
    
    // For demonstration purposes only
    // In production, use a proper BIP39 implementation
    const secretKeyBase58 = base58Encode(new Uint8Array(this.currentWallet.secretKey));
    return secretKeyBase58;
  }
}

export default NonCustodialWalletClient;
