// Simple browser logger with environment-aware levels
// Uses Vite's import.meta.env.PROD to gate debug logs in production

const isProd = import.meta.env.PROD;

type LogFn = (...args: any[]) => void;

const noop: LogFn = () => {};

const logger = {
  debug: isProd ? noop : ((...args) => console.debug(...args)),
  info: (...args) => console.info(...args),
  warn: (...args) => console.warn(...args),
  error: (...args) => console.error(...args),
};

export default logger;

