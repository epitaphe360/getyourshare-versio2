/**
 * Logger utility for frontend
 * Provides consistent logging across the application
 */

const LOG_LEVELS = {
  DEBUG: 'debug',
  INFO: 'info',
  WARNING: 'warning',
  ERROR: 'error'
};

class Logger {
  constructor(name = 'GetYourShare') {
    this.name = name;
    this.enabled = process.env.NODE_ENV === 'development';
  }

  debug(message, ...args) {
    if (this.enabled) {
      console.debug(`[${this.name}] 🔍 ${message}`, ...args);
    }
  }

  info(message, ...args) {
    if (this.enabled) {
      console.info(`[${this.name}] ℹ️ ${message}`, ...args);
    }
  }

  warning(message, ...args) {
    console.warn(`[${this.name}] ⚠️ ${message}`, ...args);
  }

  error(message, ...args) {
    console.error(`[${this.name}] ❌ ${message}`, ...args);
  }

  log(message, ...args) {
    if (this.enabled) {

    }
  }
}

// Export singleton instance
export const logger = new Logger('GetYourShare');
export default logger;
