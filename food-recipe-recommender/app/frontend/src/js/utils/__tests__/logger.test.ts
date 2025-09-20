import { describe, it, expect } from 'vitest';
import logger from '../../utils/logger';

describe('logger', () => {
  it('exposes log methods without throwing', () => {
    expect(typeof logger.debug).toBe('function');
    expect(typeof logger.info).toBe('function');
    expect(typeof logger.warn).toBe('function');
    expect(typeof logger.error).toBe('function');

    // Calls should not throw in test env
    logger.debug('debug');
    logger.info('info');
    logger.warn('warn');
    logger.error('error');
  });
});

