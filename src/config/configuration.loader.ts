import { appConfigSchema, AppConfig } from './schemas/app.schema';
import { logConfigSchema, LogConfig } from './schemas/log.schema';
import {
  databaseConfigSchema,
  DatabaseConfig,
} from './schemas/database.schema';

export interface Configuration {
  nodeEnv: string;
  app: AppConfig;
  log: LogConfig;
  database: DatabaseConfig;
}

export default (): Configuration => {
  const nodeEnv = process.env.NODE_ENV ?? 'development';

  const app = appConfigSchema.parse({
    name: process.env.APP_NAME,
    host: process.env.HOST,
    port: process.env.PORT,
    globalPrefix: process.env.GLOBAL_PREFIX,
    enableVersioning: process.env.API_VERSIONING,
    corsOrigins: process.env.CORS_ORIGINS,
  });

  const log = logConfigSchema.parse({
    level: process.env.LOG_LEVEL,
    pretty: process.env.LOG_PRETTY,
    directory: process.env.LOG_DIRECTORY,
    maxFiles: process.env.LOG_MAX_FILES,
    maxSize: process.env.LOG_MAX_SIZE,
  });

  const database = databaseConfigSchema.parse({
    host: process.env.DB_HOST,
    port: process.env.DB_PORT,
    username: process.env.DB_USERNAME,
    password: process.env.DB_PASSWORD,
    database: process.env.DB_DATABASE,
    ssl: process.env.DB_SSL,
    poolMin: process.env.DB_POOL_MIN,
    poolMax: process.env.DB_POOL_MAX,
    connectionTimeout: process.env.DB_CONNECTION_TIMEOUT,
  });

  return {
    nodeEnv,
    app,
    log,
    database,
  };
};
