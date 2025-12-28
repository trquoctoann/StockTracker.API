import { z } from 'zod';

export const envSchema = z.object({
  // Environment
  NODE_ENV: z.enum(['development', 'production']).default('development'),

  // App
  APP_NAME: z.string().optional(),
  HOST: z.string().optional(),
  PORT: z.string().optional(),
  GLOBAL_PREFIX: z.string().optional(),
  API_VERSIONING: z.string().optional(),
  CORS_ORIGINS: z.string().optional(),

  // Logging
  LOG_LEVEL: z.string().optional(),
  LOG_PRETTY: z.string().optional(),
  LOG_DIRECTORY: z.string().optional(),
  LOG_MAX_FILES: z.string().optional(),
  LOG_MAX_SIZE: z.string().optional(),

  // Database
  DB_HOST: z.string().optional(),
  DB_PORT: z.string().optional(),
  DB_USERNAME: z.string().optional(),
  DB_PASSWORD: z.string().optional(),
  DB_DATABASE: z.string().optional(),
  DB_SSL: z.string().optional(),
  DB_POOL_MIN: z.string().optional(),
  DB_POOL_MAX: z.string().optional(),
  DB_CONNECTION_TIMEOUT: z.string().optional(),
});

export function validateEnv(config: Record<string, unknown>): Env {
  const result = envSchema.safeParse(config);

  if (!result.success) {
    const messages = result.error.issues.map(
      (issue) => `${issue.path.join('.')}: ${issue.message}`,
    );

    throw new Error(`Environment validation failed:\n${messages.join('\n')}`);
  }
  return result.data;
}

export type Env = z.infer<typeof envSchema>;
