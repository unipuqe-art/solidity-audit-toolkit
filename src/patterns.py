```javascript
/**
 * @file patterns.js
 * @module Patterns
 * @description This module contains utility functions for identifying common Solidity security patterns.
 */

const fs = require('fs');
const path = require('path');

/**
 * Scans a directory for Solidity files and returns an array of file paths.
 *
 * @param {string} dirPath - The directory path to scan.
 * @returns {Promise<Array<string>>} A promise that resolves with an array of file paths.
 */
async function findSolidityFiles(dirPath) {
  try {
    const files = await fs.promises.readdir(dirPath);
    const solidityFiles = [];

    for (const file of files) {
      const filePath = path.join(dirPath, file);

      if ((await fs.promises.stat(filePath)).isDirectory()) {
        solidityFiles.push(...(await findSolidityFiles(filePath)));
      } else if (path.extname(file).toLowerCase() === '.sol') {
        solidityFiles.push(filePath);
      }
    }

    return solidityFiles;
  } catch (error) {
    console.error(`Error scanning directory ${dirPath}:`, error);
    throw error;
  }
}

/**
 * Checks for common reentrancy patterns in Solidity code.
 *
 * @param {string} contractCode - The Solidity contract code to check.
 * @returns {Array<{ line: number, description: string }>} An array of objects containing line numbers and descriptions of detected reentrancy patterns.
 */
function checkReentrancy(contractCode) {
  const reentrancyPatterns = [
    /call.value/, // Potential direct call to external contract
    /msg.sender.transfer/, // Potential direct transfer to attacker
    /send/, // Potential direct send to attacker
  ];

  const matches = [];
  const lines = contractCode.split('\n');

  for (const pattern of reentrancyPatterns) {
    for (let i = 0; i < lines.length; i++) {
      if (pattern.test(lines[i])) {
        matches.push({
          line: i + 1,
          description: `Potential reentrancy vulnerability detected at line ${i + 1}: ${lines[i].trim()}`,
        });
      }
    }
  }

  return matches;
}

/**
 * Analyzes a Solidity contract file for security patterns.
 *
 * @param {string} filePath - The path to the Solidity contract file to analyze.
 * @returns {Promise<{ filePath: string, results: Array<{ line: number, description: string }> }>} A promise that resolves with an object containing the file path and analysis results.
 */
async function analyzeContract(filePath) {
  try {
    const contractCode = await fs.promises.readFile(filePath, 'utf8');
    const results = checkReentrancy(contractCode);

    return {
      filePath,
      results,
    };
  } catch (error) {
    console.error(`Error reading file ${filePath}:`, error);
    throw error;
  }
}

/**
 * Analyzes all Solidity contracts in a directory for security patterns.
 *
 * @param {string} dirPath - The directory path containing the Solidity contracts to analyze.
 * @returns {Promise<Array<{ filePath: string, results: Array<{ line: number, description: string }> }>>} A promise that resolves with an array of objects containing file paths and analysis results.
 */
async function analyzeDirectory(dirPath) {
  try {
    const files = await findSolidityFiles(dirPath);
    const results = [];

    for (const file of files) {
      results.push(await analyzeContract(file));
    }

    return results;
  } catch (error) {
    console.error(`Error analyzing directory ${dirPath}:`, error);
    throw error;
  }
}

module.exports = {
  findSolidityFiles,
  checkReentrancy,
  analyzeContract,
  analyzeDirectory,
};
```