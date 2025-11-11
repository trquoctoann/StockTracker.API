export default () => ({
  nodeEnv: process.env.NODE_ENV ?? 'development',
  app: {
    name: process.env.APP_NAME ?? 'StockTracker.API',
    host: process.env.HOST ?? '0.0.0.0',
    port: Number(process.env.PORT ?? 3000),
    globalPrefix: process.env.GLOBAL_PREFIX ?? 'api',
    enableVersioning: (process.env.API_VERSIONING ?? 'true') === 'true',
    corsOrigins: (process.env.CORS_ORIGINS ?? '*')
      .split(',')
      .map((x) => x.trim())
      .filter((x) => x.length > 0),
  },
  log: {
    level: process.env.LOG_LEVEL ?? 'info',
    pretty: (process.env.LOG_PRETTY ?? 'true') === 'true',
  },
});
